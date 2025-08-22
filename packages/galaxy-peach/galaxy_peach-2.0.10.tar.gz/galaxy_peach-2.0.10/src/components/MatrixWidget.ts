import { Widget } from '@lumino/widgets';
import * as d3 from 'd3';
import { LABEL_MAP } from './labelMap';
import { STAGE_GROUP_MAP } from './stage_hierarchy';
import { analytics } from '../analytics/posthog-config';

type Cell = {
    cellId: number;
    cellType: string;
    "1st-level label": string;
};

type Notebook = {
    cells: Cell[];
    globalIndex?: number;
};



export class MatrixWidget extends Widget {
    private data: Notebook[];
    private colorScale: (label: string) => string;
    private sortState: number = 0; // 0: 默认, 1: notebook长度降序, 2: notebook长度升序, 3: similarity排序
    private voteEnabled: boolean = false; // 独立的投票排序状态
    private lengthSortEnabled: boolean = true; // 独立的长度排序状态，默认激活
    private clusterSizeSortDirection: 'desc' | 'asc' = 'asc'; // cluster size排序方向，默认升序
    private notebookOrder: number[] = [];
    private sortButton: HTMLButtonElement;
    private similaritySortButton: HTMLButtonElement;
    private voteSortButton!: HTMLButtonElement; // 投票排序按钮
    private cellHeightButton: HTMLButtonElement; // cell高度模式按钮
    private markdownButton: HTMLButtonElement; // markdown显示/隐藏按钮

    private similarityGroups: any[];
    private voteData: any[] = []; // 投票数据
    private cellHeightMode: 'fixed' | 'dynamic' = 'fixed'; // cell高度模式：固定、动态
    private showMarkdown: boolean = false; // markdown显示状态
    private kernelTitleMap: Map<string, { title: string; creationDate: string; totalLines: number; displayname?: string; url?: string }> = new Map(); // 存储kernelVersionId到Title的映射
    private selectedClusterId: string | null = null; // 当前选中的cluster ID
    private clusterInfoContainer: HTMLDivElement | null = null; // cluster信息容器
    private topStats: { topStages?: [string, number][], topTransitions?: [string, number][] } = {}; // 存储top stages和top transitions
    private _topStatsHandler: (e: any) => void; // 事件处理函数引用
    private summaryData: any = null; // 存储summary数据
    private competitionInfo: { id: string; name: string; url: string; description?: string; category?: string; evaluation?: string; startDate?: string; endDate?: string } | null = null; // 存储competition信息
    private stageHoverTimeout: number | null = null; // stage hover防抖定时器
    private transitionHoverTimeout: number | null = null; // transition hover防抖定时器

    // 获取cluster的title
    private getClusterTitle(clusterId: string): string {
        if (this.summaryData && this.summaryData.analysis_sections &&
            this.summaryData.analysis_sections.cluster_titles &&
            this.summaryData.analysis_sections.cluster_titles.structured) {
            const clusterTitles = this.summaryData.analysis_sections.cluster_titles.structured;
            const title = clusterTitles[clusterId];
            if (title) {
                // 移除引号
                const cleanTitle = title.replace(/^"|"$/g, '');
                return cleanTitle;
            }
        }
        return `Cluster ${clusterId}`;
    }

    // 检查notebook是否属于选中的cluster
    private isNotebookInSelectedCluster(notebook: any): boolean {
        if (!this.selectedClusterId || this.sortState !== 3 || !this.similarityGroups || this.similarityGroups.length === 0) {
            return true; // 如果没有选中cluster，返回true表示所有notebook都应该被考虑
        }

        const kernelId = notebook?.kernelVersionId?.toString();
        const simRow = kernelId ? this.similarityGroups.find((row: any) => row.kernelVersionId === kernelId) : null;
        return simRow && simRow.cluster_id === this.selectedClusterId;
    }

    constructor(data: Notebook[], colorScale: (label: string) => string, similarityGroups?: any[], kernelTitleMap?: Map<string, { title: string; creationDate: string; totalLines: number; displayname?: string; url?: string }>, voteData?: any[], summaryData?: any, competitionInfo?: { id: string; name: string; url: string; description?: string; category?: string; evaluation?: string; startDate?: string; endDate?: string }) {
        super();
        this.data = data.map((nb, i) => ({ ...nb, globalIndex: i + 1 }));
        this.colorScale = colorScale;
        this.similarityGroups = similarityGroups || [];
        this.voteData = voteData || [];
        this.kernelTitleMap = kernelTitleMap || new Map();
        this.summaryData = summaryData || null;
        this.competitionInfo = competitionInfo || null;



        // 初始化时重置状态，确保每次创建都是全新的状态
        this.resetState();
        this.id = 'matrix-widget';
        this.title.label = 'Overview';
        this.title.closable = true;
        this.addClass('matrix-widget');

        // ====== DROPLISTS FOR FILTERING ======
        // Collect unique assignments and student_ids
        const assignments = Array.from(new Set(this.data.map(nb => (nb as any).assignment).filter(Boolean)));
        const studentIds = Array.from(new Set(this.data.map(nb => (nb as any).student_id).filter(Boolean)));

        // Assignment dropdown
        const assignmentSelect = document.createElement('select');
        assignmentSelect.style.marginRight = '12px';
        assignmentSelect.innerHTML = `<option value="">All Assignments</option>` +
            assignments.map(a => `<option value="${a}">${a}</option>`).join('');

        // Student ID dropdown
        const studentSelect = document.createElement('select');
        studentSelect.innerHTML = `<option value="">All Students</option>` +
            studentIds.map(s => `<option value="${s}">${s}</option>`).join('');

        // Add to DOM
        const filterBar = document.createElement('div');
        filterBar.style.margin = '8px 0';
        filterBar.style.display = 'none'; // 隐藏 droplists
        filterBar.appendChild(assignmentSelect);
        filterBar.appendChild(studentSelect);
        this.node.appendChild(filterBar);

        // ====== CLUSTER INFO AREA ======
        this.clusterInfoContainer = document.createElement('div');
        this.clusterInfoContainer.className = 'cluster-info-container';
        this.clusterInfoContainer.style.display = 'none'; // 默认隐藏
        this.clusterInfoContainer.style.padding = '16px 12px 12px 12px';
        this.clusterInfoContainer.style.borderBottom = '1px solid #e9ecef';
        this.clusterInfoContainer.style.backgroundColor = '#ffffff';
        this.clusterInfoContainer.style.fontSize = '14px';
        this.clusterInfoContainer.style.lineHeight = '1.5';
        this.clusterInfoContainer.style.borderRadius = '0';
        this.clusterInfoContainer.style.boxShadow = 'none';
        this.clusterInfoContainer.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        this.clusterInfoContainer.style.color = '#222';
        this.clusterInfoContainer.style.boxSizing = 'border-box';
        this.clusterInfoContainer.style.width = '100%';
        this.node.appendChild(this.clusterInfoContainer);

        // Store filter state
        (this as any)._assignmentFilter = '';
        (this as any)._studentFilter = '';

        // Listen for changes
        assignmentSelect.onchange = () => {
            // 保存当前的cluster选择状态
            const currentSelectedCluster = this.selectedClusterId;

            (this as any)._assignmentFilter = assignmentSelect.value;
            this.saveFilterState();
            this.drawMatrix();

            // 恢复高亮状态 - 由于matrix不再跟随notebook detail tab的选择，这里不再恢复高亮状态

            // 如果有选中的cluster且在cluster模式下，滚动到cluster位置
            if (currentSelectedCluster && this.sortState === 3) {
                setTimeout(() => {
                    this.scrollToCluster();
                }, 200); // 给足够时间让DOM更新
            }

            // 派发筛选事件和cluster选择事件
            const filteredNotebooks = this.getFilteredNotebooks();
            window.dispatchEvent(new CustomEvent('galaxy-matrix-filtered', { detail: { notebooks: filteredNotebooks } }));

            // 如果在cluster模式下，派发cluster选择事件以更新左边的flowchart
            if (this.sortState === 3) {
                const clusterFilteredNotebooks = this.getClusterFilteredNotebooks();
                window.dispatchEvent(new CustomEvent('galaxy-cluster-selected', {
                    detail: {
                        clusterId: this.selectedClusterId,
                        notebooks: clusterFilteredNotebooks
                    }
                }));
            }
        };
        studentSelect.onchange = () => {
            // 保存当前的cluster选择状态
            const currentSelectedCluster = this.selectedClusterId;

            (this as any)._studentFilter = studentSelect.value;
            this.saveFilterState();
            this.drawMatrix();

            // 恢复高亮状态 - 由于matrix不再跟随notebook detail tab的选择，这里不再恢复高亮状态

            // 如果有选中的cluster且在cluster模式下，滚动到cluster位置
            if (currentSelectedCluster && this.sortState === 3) {
                setTimeout(() => {
                    this.scrollToCluster();
                }, 200); // 给足够时间让DOM更新
            }

            // 派发筛选事件和cluster选择事件
            const filteredNotebooks = this.getFilteredNotebooks();
            window.dispatchEvent(new CustomEvent('galaxy-matrix-filtered', { detail: { notebooks: filteredNotebooks } }));

            // 如果在cluster模式下，派发cluster选择事件以更新左边的flowchart
            if (this.sortState === 3) {
                const clusterFilteredNotebooks = this.getClusterFilteredNotebooks();
                window.dispatchEvent(new CustomEvent('galaxy-cluster-selected', {
                    detail: {
                        clusterId: this.selectedClusterId,
                        notebooks: clusterFilteredNotebooks
                    }
                }));
            }
        };

        // 排序按钮区域
        const sortBar = document.createElement('div');
        sortBar.style.display = 'flex';
        sortBar.style.justifyContent = 'space-between';
        sortBar.style.alignItems = 'center';
        sortBar.style.marginTop = '8px';
        sortBar.style.marginBottom = '4px';
        sortBar.style.height = '24px';
        sortBar.style.width = '100%';
        sortBar.style.position = 'relative';

        // 左侧排序按钮容器
        const leftSortButtons = document.createElement('div');
        leftSortButtons.style.display = 'flex';
        leftSortButtons.style.alignItems = 'center';
        leftSortButtons.style.gap = '8px';

        // 添加 "Sort by:" 文本标签
        const sortByLabel = document.createElement('span');
        sortByLabel.textContent = 'Sort by:';
        sortByLabel.style.fontSize = '12px';
        sortByLabel.style.fontWeight = '500';
        sortByLabel.style.color = '#666';
        sortByLabel.style.marginRight = '4px';
        leftSortButtons.appendChild(sortByLabel);

        // 右侧其他按钮容器
        const rightButtons = document.createElement('div');
        rightButtons.style.display = 'flex';
        rightButtons.style.alignItems = 'center';
        rightButtons.style.gap = '8px';

        // 初始化notebookOrder
        this.notebookOrder = this.data.map((_, i) => i);

        // 1. Cluster按钮 (移到右边)
        this.similaritySortButton = document.createElement('button');
        this.similaritySortButton.style.background = 'none';
        this.similaritySortButton.style.border = 'none';
        this.similaritySortButton.style.cursor = 'pointer';
        this.similaritySortButton.style.fontSize = '18px';
        this.similaritySortButton.style.display = 'flex';
        this.similaritySortButton.style.alignItems = 'center';
        this.similaritySortButton.style.justifyContent = 'center';
        this.similaritySortButton.style.transition = 'transform 0.2s ease';
        this.similaritySortButton.innerHTML = this.getSimilaritySortIcon();

        // Add hover effects
        this.similaritySortButton.onmouseenter = () => {
            this.similaritySortButton.style.transform = 'scale(1.1)';
        };
        this.similaritySortButton.onmouseleave = () => {
            this.similaritySortButton.style.transform = 'scale(1)';
        };
        this.similaritySortButton.onclick = () => {
            // 由于matrix不再跟随notebook detail tab的选择，这里不再保存高亮状态

            if (this.sortState === 3) {
                // 取消cluster时，重置length排序状态，但清除cluster选择
                this.sortState = 0;
                this.selectedClusterId = null; // 关闭cluster模式时清除选择
                this.similaritySortButton.classList.remove('active');
                if (!this.voteEnabled) {
                    // vote未激活时，length应该为默认状态的激活状态
                    this.lengthSortEnabled = true;
                    this.sortState = 0; // 默认状态但激活
                } else {
                    // vote激活时，length未激活
                    this.lengthSortEnabled = false;
                    this.sortState = 0;
                }
            } else {
                // 激活cluster时，启用length排序（默认升序）
                this.sortState = 3;
                this.similaritySortButton.classList.add('active');
                if (!this.voteEnabled) {
                    // vote未激活时，length应该激活
                    this.lengthSortEnabled = true;
                    this.clusterSizeSortDirection = 'asc'; // 默认升序
                } else {
                    // vote激活时，length未激活
                    this.lengthSortEnabled = false;
                }
            }
            this.updateNotebookOrder();
            this.similaritySortButton.innerHTML = this.getSimilaritySortIcon();
            this.sortButton.innerHTML = this.getSortIcon(); // 更新length按钮图标
            this.updateSortButtonState();

            // Track matrix sort change
            analytics.trackMatrixInteraction('sort_changed', {
                sortType: 'similarity_clustering',
                sortState: this.sortState,
                lengthSortEnabled: this.lengthSortEnabled,
                clusterMode: this.sortState === 3,
                selectedClusterId: this.selectedClusterId,
                interaction_context: 'similarity_clustering'
            });

            this.saveFilterState();
            this.drawMatrix();

            // 由于matrix不再跟随notebook detail tab的选择，这里不再恢复高亮状态

            // 派发筛选事件和cluster选择事件
            const filteredNotebooks = this.getFilteredNotebooks();
            window.dispatchEvent(new CustomEvent('galaxy-matrix-filtered', { detail: { notebooks: filteredNotebooks } }));

            // 派发cluster选择事件以更新左边的flowchart
            const clusterFilteredNotebooks = this.getClusterFilteredNotebooks();
            window.dispatchEvent(new CustomEvent('galaxy-cluster-selected', {
                detail: {
                    clusterId: this.selectedClusterId,
                    notebooks: clusterFilteredNotebooks
                }
            }));
        };

        // 2. Vote按钮 (第二个)
        this.voteSortButton = document.createElement('button');
        this.voteSortButton.style.background = 'none';
        this.voteSortButton.style.border = 'none';
        this.voteSortButton.style.cursor = 'pointer';
        this.voteSortButton.style.fontSize = '18px';
        this.voteSortButton.style.display = 'flex';
        this.voteSortButton.style.alignItems = 'center';
        this.voteSortButton.style.justifyContent = 'center';
        this.voteSortButton.innerHTML = this.getVoteSortIcon();

        // Add hover effects
        this.voteSortButton.style.transition = 'transform 0.2s ease';
        this.voteSortButton.addEventListener('mouseenter', () => {
            this.voteSortButton.style.transform = 'scale(1.1)';
        });
        this.voteSortButton.addEventListener('mouseleave', () => {
            this.voteSortButton.style.transform = 'scale(1)';
        });
        this.voteSortButton.onclick = () => {
            // 保存当前的cluster选择状态
            const currentSelectedCluster = this.selectedClusterId;

            this.voteEnabled = !this.voteEnabled;
            if (this.voteEnabled) {
                this.voteSortButton.classList.add('active');
                // vote激活时，length排序设置为未激活
                this.lengthSortEnabled = false;
                if (this.sortState !== 3) {
                    this.sortState = 0; // 非cluster模式下重置sortState
                } else {
                    // cluster激活时，设置length为从少到多的未激活状态
                    this.clusterSizeSortDirection = 'asc'; // 从少到多
                }
            } else {
                this.voteSortButton.classList.remove('active');
                // vote未激活时，length排序设置为默认状态的激活状态
                this.lengthSortEnabled = true;
                if (this.sortState === 3) {
                    // cluster激活时，默认升序
                    this.clusterSizeSortDirection = 'asc';
                } else {
                    // cluster未激活时，默认激活状态
                    this.sortState = 0;
                }
            }
            this.updateNotebookOrder();
            this.similaritySortButton.innerHTML = this.getSimilaritySortIcon();
            this.voteSortButton.innerHTML = this.getVoteSortIcon();
            this.sortButton.innerHTML = this.getSortIcon(); // 更新length按钮图标
            this.updateSortButtonState();

            // Track matrix sort change
            analytics.trackMatrixInteraction('sort_changed', {
                sortType: 'vote_sort',
                voteEnabled: this.voteEnabled,
                sortState: this.sortState,
                lengthSortEnabled: this.lengthSortEnabled,
                isClusterMode: this.sortState === 3,
                interaction_context: 'vote_based_sorting'
            });

            this.saveFilterState();
            this.drawMatrix();

            // 由于matrix不再跟随notebook detail tab的选择，这里不再恢复高亮状态

            // 如果有选中的cluster且在cluster模式下，滚动到cluster位置
            if (currentSelectedCluster && this.sortState === 3) {
                setTimeout(() => {
                    this.scrollToCluster();
                }, 200); // 给足够时间让DOM更新
            }

            // 派发筛选事件和cluster选择事件
            const filteredNotebooks = this.getFilteredNotebooks();
            window.dispatchEvent(new CustomEvent('galaxy-matrix-filtered', { detail: { notebooks: filteredNotebooks } }));

            // 如果在cluster模式下，派发cluster选择事件以更新左边的flowchart
            if (this.sortState === 3) {
                const clusterFilteredNotebooks = this.getClusterFilteredNotebooks();
                window.dispatchEvent(new CustomEvent('galaxy-cluster-selected', {
                    detail: {
                        clusterId: this.selectedClusterId,
                        notebooks: clusterFilteredNotebooks
                    }
                }));
            }
        };
        leftSortButtons.appendChild(this.voteSortButton);

        // 3. Length按钮 (第三个)
        this.sortButton = document.createElement('button');
        this.sortButton.style.background = 'none';
        this.sortButton.style.border = 'none';
        this.sortButton.style.cursor = 'pointer';
        this.sortButton.style.fontSize = '18px';
        this.sortButton.style.display = 'flex';
        this.sortButton.style.alignItems = 'center';
        this.sortButton.style.justifyContent = 'center';
        this.sortButton.innerHTML = this.getSortIcon();

        // Add hover effects
        this.sortButton.style.transition = 'transform 0.2s ease';
        this.sortButton.addEventListener('mouseenter', () => {
            this.sortButton.style.transform = 'scale(1.1)';
        });
        this.sortButton.addEventListener('mouseleave', () => {
            this.sortButton.style.transform = 'scale(1)';
        });
        this.sortButton.onclick = () => {
            // 保存当前的cluster选择状态
            const currentSelectedCluster = this.selectedClusterId;

            // 切换length排序状态
            if (this.sortState === 3) {
                // cluster激活时：只切换升序/降序，不关闭排序
                if (!this.lengthSortEnabled) {
                    // 从未激活状态开始：激活升序（默认）
                    this.lengthSortEnabled = true;
                    this.clusterSizeSortDirection = 'asc';
                    // length激活时，vote排序设置为未激活
                    this.voteEnabled = false;
                    this.voteSortButton.classList.remove('active');
                } else {
                    // 已激活状态：切换升序/降序
                    this.clusterSizeSortDirection = this.clusterSizeSortDirection === 'asc' ? 'desc' : 'asc';
                }
            } else {
                // cluster未激活时：默认激活 -> 降序 -> 升序 -> 默认激活
                // 确保length排序被激活
                this.lengthSortEnabled = true;

                // 如果当前vote激活，则先回到length的默认激活状态
                if (this.voteEnabled) {
                    this.sortState = 0; // 回到默认激活状态
                } else {
                    // 正常的length排序循环：默认激活 -> 降序 -> 升序 -> 默认激活
                    if (this.sortState === 0) {
                        // 默认激活状态：切换到降序
                        this.sortState = 1;
                    } else if (this.sortState === 1) {
                        // 当前是降序：切换到升序
                        this.sortState = 2;
                    } else if (this.sortState === 2) {
                        // 当前是升序：切换回默认激活
                        this.sortState = 0;
                    }
                }
                // length激活时，vote排序设置为未激活
                this.voteEnabled = false;
                this.voteSortButton.classList.remove('active');
            }

            this.updateNotebookOrder();
            this.sortButton.innerHTML = this.getSortIcon();
            this.voteSortButton.innerHTML = this.getVoteSortIcon(); // 更新vote按钮图标
            this.updateSortButtonState();

            // Track matrix sort change
            analytics.trackMatrixInteraction('sort_changed', {
                sortType: 'length_sort',
                sortState: this.sortState,
                lengthSortEnabled: this.lengthSortEnabled,
                clusterSizeSortDirection: this.clusterSizeSortDirection,
                isClusterMode: this.sortState === 3,
                interaction_context: 'notebook_length_sorting'
            });

            this.saveFilterState();
            this.drawMatrix();

            // 由于matrix不再跟随notebook detail tab的选择，这里不再恢复高亮状态

            // 如果有选中的cluster且在cluster模式下，滚动到cluster位置
            if (currentSelectedCluster && this.sortState === 3) {
                setTimeout(() => {
                    this.scrollToCluster();
                }, 200); // 给足够时间让DOM更新
            }

            // 派发筛选事件和cluster选择事件
            const filteredNotebooks = this.getFilteredNotebooks();
            window.dispatchEvent(new CustomEvent('galaxy-matrix-filtered', { detail: { notebooks: filteredNotebooks } }));

            // 如果在cluster模式下，派发cluster选择事件以更新左边的flowchart
            if (this.sortState === 3) {
                const clusterFilteredNotebooks = this.getClusterFilteredNotebooks();
                window.dispatchEvent(new CustomEvent('galaxy-cluster-selected', {
                    detail: {
                        clusterId: this.selectedClusterId,
                        notebooks: clusterFilteredNotebooks
                    }
                }));
            }
        };
        leftSortButtons.appendChild(this.sortButton);

        // cell高度模式按钮
        this.cellHeightButton = document.createElement('button');
        this.cellHeightButton.style.background = 'none';
        this.cellHeightButton.style.border = 'none';
        this.cellHeightButton.style.cursor = 'pointer';
        this.cellHeightButton.style.fontSize = '18px';
        this.cellHeightButton.style.display = 'flex';
        this.cellHeightButton.style.alignItems = 'center';
        this.cellHeightButton.style.justifyContent = 'center';
        this.cellHeightButton.innerHTML = this.getCellHeightIcon();

        // Add hover effects using addEventListener to avoid conflict with tooltip
        this.cellHeightButton.style.transition = 'transform 0.2s ease';
        this.cellHeightButton.addEventListener('mouseenter', () => {
            this.cellHeightButton.style.transform = 'scale(1.1)';
        });
        this.cellHeightButton.addEventListener('mouseleave', () => {
            this.cellHeightButton.style.transform = 'scale(1)';
        });
        this.cellHeightButton.onclick = () => {
            // 保存当前的cluster选择状态
            const currentSelectedCluster = this.selectedClusterId;

            // 在两种模式之间切换：fixed -> dynamic -> fixed
            if (this.cellHeightMode === 'fixed') {
                this.cellHeightMode = 'dynamic';
            } else {
                this.cellHeightMode = 'fixed';
            }
            this.cellHeightButton.innerHTML = this.getCellHeightIcon();
            this.updateSortButtonState();

            // Track cell height mode change
            analytics.trackMatrixInteraction('icon_click', {
                iconType: 'cell_height',
                cellHeightMode: this.cellHeightMode,
                previousMode: this.cellHeightMode === 'fixed' ? 'dynamic' : 'fixed',
                interaction_context: 'cell_height_toggle'
            });

            this.saveFilterState();
            this.drawMatrix();

            // 由于matrix不再跟随notebook detail tab的选择，这里不再恢复高亮状态

            // 如果有选中的cluster且在cluster模式下，滚动到cluster位置
            if (currentSelectedCluster && this.sortState === 3) {
                setTimeout(() => {
                    this.scrollToCluster();
                }, 200); // 给足够时间让DOM更新
            }
        };
        rightButtons.appendChild(this.cellHeightButton);

        // markdown显示/隐藏按钮
        this.markdownButton = document.createElement('button');
        this.markdownButton.style.background = 'none';
        this.markdownButton.style.border = 'none';
        this.markdownButton.style.cursor = 'pointer';
        this.markdownButton.style.fontSize = '18px';
        this.markdownButton.style.display = 'flex';
        this.markdownButton.style.alignItems = 'center';
        this.markdownButton.style.justifyContent = 'center';
        this.markdownButton.innerHTML = this.getMarkdownIcon();

        // Add hover effects
        this.markdownButton.style.transition = 'transform 0.2s ease';
        this.markdownButton.addEventListener('mouseenter', () => {
            this.markdownButton.style.transform = 'scale(1.1)';
        });
        this.markdownButton.addEventListener('mouseleave', () => {
            this.markdownButton.style.transform = 'scale(1)';
        });
        this.markdownButton.onclick = () => {
            // 保存当前的cluster选择状态
            const currentSelectedCluster = this.selectedClusterId;

            this.showMarkdown = !this.showMarkdown;
            this.markdownButton.innerHTML = this.getMarkdownIcon();
            this.updateSortButtonState();

            // Track markdown visibility toggle
            analytics.trackMatrixInteraction('icon_click', {
                iconType: 'markdown_toggle',
                showMarkdown: this.showMarkdown,
                action: this.showMarkdown ? 'show' : 'hide',
                interaction_context: 'markdown_visibility'
            });

            this.saveFilterState();
            this.drawMatrix();

            // 由于matrix不再跟随notebook detail tab的选择，这里不再恢复高亮状态

            // 如果有选中的cluster且在cluster模式下，滚动到cluster位置
            if (currentSelectedCluster && this.sortState === 3) {
                setTimeout(() => {
                    this.scrollToCluster();
                }, 200); // 给足够时间让DOM更新
            }
        };
        rightButtons.appendChild(this.markdownButton);

        // 添加clustering按钮到右侧最左边 (第一个位置)
        rightButtons.insertBefore(this.similaritySortButton, rightButtons.firstChild);

        // 将左右容器添加到主容器
        sortBar.appendChild(leftSortButtons);
        sortBar.appendChild(rightButtons);
        this.node.appendChild(sortBar);
        this.updateSortButtonState();

        // 统一内边距
        this.node.style.padding = '16px 16px 12px 16px';
        this.node.style.display = 'flex';
        this.node.style.flexDirection = 'column';
        this.node.style.height = '100%';

        // 监听top stats更新事件
        this._topStatsHandler = (e: any) => {
            this.topStats = e.detail;
            // 如果当前正在显示cluster信息，则更新显示
            if (this.selectedClusterId && this.clusterInfoContainer) {
                this.showSelectedClusterInfo();
            }
        };
        window.addEventListener('galaxy-top-stats-updated', this._topStatsHandler);
    }

    private getSortIcon(): string {
        // SVG图标 + 文本：ID（默认）、Size↑（升序）、Size↓（降序）
        let svgIcon = '';
        let textContent = '';
        let textColor = '#555';

        if (this.sortState === 3) {
            // cluster激活时
            if (this.voteEnabled) {
                // vote激活时，显示未激活的Size↑（灰色）
                svgIcon = `<svg width="14" height="14" viewBox="0 0 20 20" style="margin-right: 4px;"><path d="M6 17h8M8 12h4M10 7h0" stroke="#555" stroke-width="2" stroke-linecap="round"/><path d="M15 14V4m0 0l-3 3m3-3l3 3" stroke="#555" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
                textContent = 'Size↑';
            } else if (this.lengthSortEnabled) {
                // length激活时，显示排序图标
                if (this.clusterSizeSortDirection === 'desc') {
                    // cluster size降序（绿色）
                    svgIcon = `<svg width="14" height="14" viewBox="0 0 20 20" style="margin-right: 4px;"><path d="M6 7h8M8 12h4M10 17h0" stroke="#4caf50" stroke-width="2" stroke-linecap="round"/><path d="M15 4v10m0 0l-3-3m3 3l3-3" stroke="#4caf50" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
                    textContent = 'Size';
                    textColor = '#4caf50';
                } else {
                    // cluster size升序（绿色）
                    svgIcon = `<svg width="14" height="14" viewBox="0 0 20 20" style="margin-right: 4px;"><path d="M6 17h8M8 12h4M10 7h0" stroke="#4caf50" stroke-width="2" stroke-linecap="round"/><path d="M15 14V4m0 0l-3 3m3-3l3 3" stroke="#4caf50" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
                    textContent = 'Size';
                    textColor = '#4caf50';
                }
            } else {
                // 默认状态：未激活的Size↑（灰色）
                svgIcon = `<svg width="14" height="14" viewBox="0 0 20 20" style="margin-right: 4px;"><path d="M6 17h8M8 12h4M10 7h0" stroke="#555" stroke-width="2" stroke-linecap="round"/><path d="M15 14V4m0 0l-3 3m3-3l3 3" stroke="#555" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
                textContent = 'Size';
            }
        } else if (this.lengthSortEnabled) {
            // length激活时（非cluster模式）
            if (this.sortState === 1) {
                // 按notebook长度降序（绿色）
                svgIcon = `<svg width="14" height="14" viewBox="0 0 20 20" style="margin-right: 4px;"><path d="M6 7h8M8 12h4M10 17h0" stroke="#4caf50" stroke-width="2" stroke-linecap="round"/><path d="M15 4v10m0 0l-3-3m3 3l3-3" stroke="#4caf50" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
                textContent = 'Size';
                textColor = '#4caf50';
            } else if (this.sortState === 2) {
                // 按notebook长度升序（绿色）
                svgIcon = `<svg width="14" height="14" viewBox="0 0 20 20" style="margin-right: 4px;"><path d="M6 17h8M8 12h4M10 7h0" stroke="#4caf50" stroke-width="2" stroke-linecap="round"/><path d="M15 14V4m0 0l-3 3m3-3l3 3" stroke="#4caf50" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
                textContent = 'Size';
                textColor = '#4caf50';
            } else {
                // 默认激活状态：ID（绿色）
                svgIcon = `<svg width="18" height="18" viewBox="0 0 1024 1024" style="margin-right: 4px;"><path d="M404.05 177.6H301.23v569.64H254.9l98.16 103.5 101.28-103.5h-50.28V177.6z m216.36 264.55h56.25V189.03h-56.25c-14.85 32.81-41.8 57.42-80.86 73.83v31.64c32.03-4.69 58.98-14.83 80.86-30.47v178.12z m14.07 93.36c-57.82 2.34-88.68 32.04-92.58 89.06 2.34 50.79 32.41 76.96 90.23 78.52 17.96 0.79 33.98-4.28 48.05-15.23 0.77 49.22-18.37 74.23-57.42 75-29.7-0.77-54.69-13.28-75-37.5v38.67c21.09 21.86 50.39 32.81 87.89 32.81 66.39 0 99.61-42.96 99.61-128.91 1.55-91.4-32.05-135.53-100.78-132.42z m3.51 132.42c-25.78-0.77-39.07-16.79-39.84-48.05 1.56-30.47 14.45-46.47 38.67-48.05 25.78 1.58 39.06 18.37 39.84 50.39-1.57 28.92-14.46 44.16-38.67 45.71z" fill="#4caf50"/></svg>`;
                textContent = 'ID';
                textColor = '#4caf50';
            }
        } else {
            // length未激活状态：ID（灰色）
            svgIcon = `<svg width="18" height="18" viewBox="0 0 1024 1024" style="margin-right: 4px;"><path d="M404.05 177.6H301.23v569.64H254.9l98.16 103.5 101.28-103.5h-50.28V177.6z m216.36 264.55h56.25V189.03h-56.25c-14.85 32.81-41.8 57.42-80.86 73.83v31.64c32.03-4.69 58.98-14.83 80.86-30.47v178.12z m14.07 93.36c-57.82 2.34-88.68 32.04-92.58 89.06 2.34 50.79 32.41 76.96 90.23 78.52 17.96 0.79 33.98-4.28 48.05-15.23 0.77 49.22-18.37 74.23-57.42 75-29.7-0.77-54.69-13.28-75-37.5v38.67c21.09 21.86 50.39 32.81 87.89 32.81 66.39 0 99.61-42.96 99.61-128.91 1.55-91.4-32.05-135.53-100.78-132.42z m3.51 132.42c-25.78-0.77-39.07-16.79-39.84-48.05 1.56-30.47 14.45-46.47 38.67-48.05 25.78 1.58 39.06 18.37 39.84 50.39-1.57 28.92-14.46 44.16-38.67 45.71z" fill="#555"/></svg>`;
            textContent = 'ID';
        }

        return `<div style="display: flex; align-items: center; justify-content: center;">${svgIcon}<span style="color: ${textColor}; font-weight: 600; font-size: 12px; line-height: 1;">${textContent}</span></div>`;
    }
    private getSimilaritySortIcon(): string {
        // clustering button: SVG图标 + 文本，激活绿色，未激活灰色
        let svgIcon = '';
        let textColor = '#555';

        if (this.sortState === 3) {
            // 激活（绿色）
            svgIcon = `<svg width="14" height="14" viewBox="0 0 24 24" style="margin-right: 4px;">
  <rect x="3" y="5" width="7" height="14" rx="2" fill="none" stroke="#4caf50" stroke-width="2"/>
  <rect x="14" y="5" width="7" height="14" rx="2" fill="none" stroke="#4caf50" stroke-width="2" stroke-dasharray="4 2"/>
  <path d="M10 12h4" stroke="#4caf50" stroke-width="2" stroke-linecap="round"/>
  <polygon points="12,10 10,12 12,14" fill="#4caf50"/>
  <polygon points="14,10 16,12 14,14" fill="#4caf50"/>
</svg>`;
            textColor = '#4caf50';
        } else {
            // 未激活（灰色）
            svgIcon = `<svg width="14" height="14" viewBox="0 0 24 24" style="margin-right: 4px;">
  <rect x="3" y="5" width="7" height="14" rx="2" fill="none" stroke="#555" stroke-width="2"/>
  <rect x="14" y="5" width="7" height="14" rx="2" fill="none" stroke="#555" stroke-width="2" stroke-dasharray="4 2"/>
  <path d="M10 12h4" stroke="#555" stroke-width="2" stroke-linecap="round"/>
  <polygon points="12,10 10,12 12,14" fill="#555"/>
  <polygon points="14,10 16,12 14,14" fill="#555"/>
</svg>`;
        }

        return `<div style="display: flex; align-items: center; justify-content: center;">${svgIcon}<span style="color: ${textColor}; font-weight: 600; font-size: 12px; line-height: 1;">Cluster</span></div>`;
    }

    private getVoteSortIcon(): string {
        // 投票排序：使用提供的SVG图标 + 文本，激活绿色，未激活灰色
        let textColor = '#555';
        const fillColor = this.voteEnabled ? '#4caf50' : '#555';

        if (this.voteEnabled) {
            textColor = '#4caf50';
        }

        const svgIcon = `<svg width="14" height="14" viewBox="0 0 1041 1024" style="margin-right: 4px;">
  <path d="M1040.968463 609.919147" fill="${fillColor}"></path>
  <path d="M1040.968463 609.919147" fill="${fillColor}"></path>
  <path d="M205.00814 443.107957c14.112416 0 25.535583-11.440563 25.535583-25.52535 0-14.103206-11.423167-25.555026-25.535583-25.555026-0.260943 0-0.475837 0.146333-0.718361 0.146333l-61.034075 0.14224c-1.39579-0.187265-2.836605-0.288572-4.272303-0.288572-19.213597 0-34.790364 15.765055-34.790364 35.274388l-0.333598 423.205675c0 19.487843 15.594163 34.763758 34.83539 34.763758 1.87572 0 3.718695 0.287549 5.516644 0l59.60247 0.026606c0.096191 0 0.14224 0.046049 0.242524 0.046049 0.092098 0 0.14224-0.046049 0.237407-0.046049l0.718361 0 0-0.147356c13.101389-0.525979 23.608697-11.157107 23.608697-24.378224 0-13.242606-10.508331-23.86964-23.608697-24.399713l0-0.38067-49.758264 0 1.413186-392.886135L205.00814 443.10591 205.00814 443.107957 205.00814 443.107957zM924.149874 406.52476c-18.839067-30.708396-46.236044-43.143613-79.397305-44.48312-1.724271-0.242524-3.449565-0.388856-5.251607-0.388856l-200.646809-0.672312c13.143345-38.143739 22.167882-83.587744 22.167882-126.296451 0-27.685549-3.119037-54.652737-8.832156-80.612992l-0.476861 0.045025c-10.392698-45.490054-50.53086-79.415724-98.609879-79.415724-55.9288 0-93.239568 47.028083-93.239568 103.652731 0 3.165086-0.283456 6.235005 0 9.309016-2.927679 105.851816-89.109504 190.976566-191.652971 202.659653l0 53.605895-0.76748 217.036082 0 224.381373 10.456143 0 488.348324 0.218988 8.549723-0.237407c18.902512 0.046049 29.528524-4.707209 46.683229-15.741519 16.295128-10.511401 28.555359-24.904203 36.614919-41.170678 2.209318-3.266393 3.935636-6.90834 4.985548-10.93812L938.303222 481.186204c1.029446-3.956102 1.316995-7.986905 1.029446-11.875468C940.869674 448.02699 936.12051 426.054559 924.149874 406.52476L924.149874 406.52476 924.149874 406.52476zM892.214535 458.177164l-81.047898 359.193779-0.092098-0.046049c-2.501984 5.996574-6.720052 11.320836-12.570293 15.068184-4.085038 2.659573-8.573259 4.245697-13.107529 4.849448-1.464351-0.192382-2.977821 0-4.50971 0l-465.886753-0.531096-0.172939-397.895219c87.24197-39.327704 151.22726-77.809133 184.196139-169.602769 0.072655 0.022513 0.122797 0.046049 0.191358 0.068562 2.928702-8.924253 6.16542-20.252253 8.492418-32.387641 5.425569-28.509311 5.135974-56.767911 5.135974-56.767911-4.821819-37.090756 25.340131-51.729152 43.330878-51.729152 24.711821 0.842181 49.091068 32.868595 49.091068 51.102888 0 0 5.466502 26.922163 5.517667 55.856146 0.046049 36.491099-4.560876 55.516408-4.560876 55.516408l-0.452301 0c-5.736655 30.160927-15.838733 58.734706-29.757744 84.937484l0.36225 0.338714c-2.301416 4.702092-3.623527 9.981329-3.623527 15.567557 0 19.460214 18.645662 21.23872 37.858236 21.23872l233.191016 0.261966c0 0 14.3181 0.452301 14.346753 0.452301l0 0.101307c11.847839-0.627287 23.654746 5.081739 30.375821 16.022928 5.374404 8.806573 6.28617 19.150152 3.402493 28.308743L892.214535 458.177164 892.214535 458.177164 892.214535 458.177164zM277.899264 885.443317c0.316202 0.024559 0.433882 0.024559 0.292666-0.024559 0.237407-0.046049 0.357134-0.072655-0.292666-0.072655-0.64059 0-0.520863 0.026606-0.25992 0.072655C277.519618 885.467877 277.615808 885.467877 277.899264 885.443317L277.899264 885.443317 277.899264 885.443317zM277.899264 885.443317" fill="${fillColor}"></path>
</svg>`;

        return `<div style="display: flex; align-items: center; justify-content: center;">${svgIcon}<span style="color: ${textColor}; font-weight: 600; font-size: 12px; line-height: 1;">Votes</span></div>`;
    }

    private getCellHeightIcon(): string {
        // cell高度模式：SVG图标 + 文本，固定高度时灰色，动态高度时绿色
        let svgIcon = '';
        let textColor = '#555';

        if (this.cellHeightMode === 'fixed') {
            // 固定高度模式：等号图标（灰色）
            svgIcon = `<svg width="14" height="14" viewBox="0 0 20 20" style="margin-right: 4px;">
  <path d="M4 8h12M4 12h12" stroke="#555" stroke-width="2" stroke-linecap="round"/>
</svg>`;
        } else {
            // 动态高度模式：波浪线图标（绿色）
            svgIcon = `<svg width="14" height="14" viewBox="0 0 20 20" style="margin-right: 4px;">
  <path d="M3 8c1-1 2-1 3 0s2 1 3 0 2-1 3 0 2 1 3 0 2-1 3 0 2 1 3 0 2-1 3 0" stroke="#4caf50" stroke-width="2" stroke-linecap="round" fill="none"/>
  <path d="M3 12c1-1 2-1 3 0s2 1 3 0 2-1 3 0 2 1 3 0 2-1 3 0 2 1 3 0 2-1 3 0" stroke="#4caf50" stroke-width="2" stroke-linecap="round" fill="none"/>
</svg>`;
            textColor = '#4caf50';
        }

        return `<div style="display: flex; align-items: center; justify-content: center;">${svgIcon}<span style="color: ${textColor}; font-weight: 600; font-size: 12px; line-height: 1;">Height</span></div>`;
    }

    private getMarkdownIcon(): string {
        // markdown显示/隐藏：SVG图标 + 文本，显示时绿色，隐藏时灰色
        let svgIcon = '';
        let textColor = '#555';

        if (this.showMarkdown) {
            // 显示markdown：绿色
            svgIcon = `<svg width="14" height="14" viewBox="0 0 1024 1024" style="margin-right: 4px;">
  <path d="M854.6 288.6L639.4 73.4c-6-6-14.1-9.4-22.6-9.4H192c-17.7 0-32 14.3-32 32v832c0 17.7 14.3 32 32 32h640c17.7 0 32-14.3 32-32V311.3c0-8.5-3.4-16.7-9.4-22.7zM790.2 326H602V137.8L790.2 326z m1.8 562H232V136h302v216c0 23.2 18.8 42 42 42h216v494z" fill="#4caf50"/>
  <path d="M429 481.2c-1.9-4.4-6.2-7.2-11-7.2h-35c-6.6 0-12 5.4-12 12v272c0 6.6 5.4 12 12 12h27.1c6.6 0 12-5.4 12-12V582.1l66.8 150.2c1.9 4.3 6.2 7.1 11 7.1H524c4.7 0 9-2.8 11-7.1l66.8-150.6V758c0 6.6 5.4 12 12 12H641c6.6 0 12-5.4 12-12V486c0-6.6-5.4-12-12-12h-34.7c-4.8 0-9.1 2.8-11 7.2l-83.1 191-83.2-191z" fill="#4caf50"/>
</svg>`;
            textColor = '#4caf50';
        } else {
            // 隐藏markdown：灰色
            svgIcon = `<svg width="14" height="14" viewBox="0 0 1024 1024" style="margin-right: 4px;">
  <path d="M854.6 288.6L639.4 73.4c-6-6-14.1-9.4-22.6-9.4H192c-17.7 0-32 14.3-32 32v832c0 17.7 14.3 32 32 32h640c17.7 0 32-14.3 32-32V311.3c0-8.5-3.4-16.7-9.4-22.7zM790.2 326H602V137.8L790.2 326z m1.8 562H232V136h302v216c0 23.2 18.8 42 42 42h216v494z" fill="#555"/>
  <path d="M429 481.2c-1.9-4.4-6.2-7.2-11-7.2h-35c-6.6 0-12 5.4-12 12v272c0 6.6 5.4 12 12 12h27.1c6.6 0 12-5.4 12-12V582.1l66.8 150.2c1.9 4.3 6.2 7.1 11 7.1H524c4.7 0 9-2.8 11-7.1l66.8-150.6V758c0 6.6 5.4 12 12 12H641c6.6 0 12-5.4 12-12V486c0-6.6-5.4-12-12-12h-34.7c-4.8 0-9.1 2.8-11 7.2l-83.1 191-83.2-191z" fill="#555"/>
</svg>`;
        }

        return `<div style="display: flex; align-items: center; justify-content: center;">${svgIcon}<span style="color: ${textColor}; font-weight: 600; font-size: 12px; line-height: 1;">Markdown</span></div>`;
    }



    private updateNotebookOrder() {
        // 创建vote map（如果需要的话）
        const voteMap = new Map();
        if (this.voteEnabled && this.voteData && this.voteData.length > 0) {
            this.voteData.forEach((row: any) => {
                if (row.kernelVersionId && row.TotalVotes !== undefined) {
                    voteMap.set(row.kernelVersionId.toString(), parseFloat(row.TotalVotes) || 0);
                }
            });
        }

        if (this.voteEnabled && this.sortState !== 3) {
            // vote激活且similarity未激活：全局按vote排序
            const arr = this.data.map((nb, i) => ({
                i,
                votes: voteMap.get((nb as any).kernelVersionId?.toString()) || 0
            }));
            arr.sort((a, b) => b.votes - a.votes);
            this.notebookOrder = arr.map(d => d.i);
        } else if (this.sortState === 0) {
            this.notebookOrder = this.data.map((_, i) => i);
        } else if (this.sortState === 1 || this.sortState === 2) {
            // 按 notebook Total Lines排序（cluster未激活时）
            const arr = this.data.map((nb, i) => ({
                i,
                totalLines: (nb as any).totalLines || nb.cells.length
            }));
            arr.sort((a, b) => this.sortState === 1 ? b.totalLines - a.totalLines : a.totalLines - b.totalLines);
            this.notebookOrder = arr.map(d => d.i);
        } else if (this.sortState === 3 && this.similarityGroups && this.similarityGroups.length > 0) {
            // similarity模式
            const groupMap: Record<string, number[]> = {};
            const ungroupedNotebooks: number[] = [];
            const clusterOrder: string[] = [];

            // 建立cluster分组
            this.similarityGroups.forEach((simRow: any) => {
                if (simRow.cluster_id && !clusterOrder.includes(simRow.cluster_id)) {
                    clusterOrder.push(simRow.cluster_id);
                    groupMap[simRow.cluster_id] = [];
                }
            });

            // 将notebook分配到clusters
            this.similarityGroups.forEach((simRow: any) => {
                if (simRow.cluster_id && simRow.kernelVersionId) {
                    const notebookIndex = this.data.findIndex((nb, i) => {
                        const kernelId = (nb as any).kernelVersionId?.toString();
                        return kernelId === simRow.kernelVersionId.toString();
                    });

                    if (notebookIndex !== -1 && groupMap[simRow.cluster_id]) {
                        if (!groupMap[simRow.cluster_id].includes(notebookIndex)) {
                            groupMap[simRow.cluster_id].push(notebookIndex);
                        }
                    }
                }
            });

            // 添加未分组的notebook
            this.data.forEach((nb, i) => {
                const kernelId = (nb as any).kernelVersionId?.toString();
                const simRow = this.similarityGroups.find((row: any) => row.kernelVersionId === kernelId);

                if (!simRow || !simRow.cluster_id) {
                    ungroupedNotebooks.push(i);
                } else {
                    const isInGroup = Object.values(groupMap).some(group => group.includes(i));
                    if (!isInGroup) {
                        ungroupedNotebooks.push(i);
                    }
                }
            });

            this.notebookOrder = [];

            // 检查是否vote激活
            if (this.voteEnabled) {
                // vote激活时，按cluster的平均vote排序，cluster内部也按vote排序
                const clusterVotes = clusterOrder.map(groupId => {
                    const notebooks = groupMap[groupId];
                    let totalVotes = 0;
                    let validNotebooks = 0;

                    // 先对cluster内部的notebook按vote排序
                    const sortedNotebooks = notebooks.map(notebookIndex => {
                        const nb = this.data[notebookIndex] as any;
                        const kernelId = nb.kernelVersionId?.toString();
                        let votes = 0;
                        if (kernelId && this.voteData && this.voteData.length > 0) {
                            const voteRow = this.voteData.find((row: any) => row.kernelVersionId === kernelId);
                            if (voteRow && voteRow.TotalVotes !== undefined) {
                                votes = parseFloat(voteRow.TotalVotes) || 0;
                            }
                        }
                        return { notebookIndex, votes };
                    }).sort((a, b) => b.votes - a.votes); // 按vote降序排序

                    // 计算cluster的平均vote
                    sortedNotebooks.forEach(({ votes }) => {
                        totalVotes += votes;
                        if (votes > 0) validNotebooks++;
                    });

                    const avgVotes = validNotebooks > 0 ? totalVotes / validNotebooks : 0;
                    return {
                        groupId,
                        avgVotes,
                        sortedNotebooks
                    };
                });

                // 按平均vote降序排序（从多到少）
                clusterVotes.sort((a, b) => b.avgVotes - a.avgVotes);

                // 使用排序后的cluster顺序，cluster内部也按vote排序
                clusterVotes.forEach(({ sortedNotebooks }) => {
                    sortedNotebooks.forEach(({ notebookIndex }) => {
                        this.notebookOrder.push(notebookIndex);
                    });
                });
            } else if (this.lengthSortEnabled) {
                // length排序激活时，按cluster size排序，cluster内部也按notebook length排序
                // 计算每个cluster的size（notebook数量）和内部排序
                const clusterSizes = clusterOrder.map(groupId => {
                    const notebooks = groupMap[groupId];

                    // 先对cluster内部的notebook按totalLines排序
                    const sortedNotebooks = notebooks.map(notebookIndex => {
                        const nb = this.data[notebookIndex] as any;
                        const totalLines = nb.totalLines || nb.cells.length; // 优先使用totalLines，如果没有则使用cells.length
                        return { notebookIndex, totalLines };
                    }).sort((a, b) => {
                        // 根据cluster size排序方向决定notebook内部排序方向
                        if (this.clusterSizeSortDirection === 'desc') {
                            return b.totalLines - a.totalLines; // 降序：长notebook在前
                        } else {
                            return a.totalLines - b.totalLines; // 升序：短notebook在前
                        }
                    });



                    return {
                        groupId,
                        size: notebooks.length,
                        sortedNotebooks
                    };
                });



                // 按cluster size排序，如果size相同则按总total length排序（支持升序和降序）
                clusterSizes.sort((a, b) => {
                    if (this.clusterSizeSortDirection === 'desc') {
                        // 降序：先按size，size相同则按总length
                        if (b.size !== a.size) {
                            return b.size - a.size; // 大cluster在前
                        } else {
                            // size相同，按总total length排序
                            const aTotalLength = a.sortedNotebooks.reduce((sum, nb) => sum + nb.totalLines, 0);
                            const bTotalLength = b.sortedNotebooks.reduce((sum, nb) => sum + nb.totalLines, 0);
                            return bTotalLength - aTotalLength; // 总length大的在前
                        }
                    } else {
                        // 升序：先按size，size相同则按总length
                        if (a.size !== b.size) {
                            return a.size - b.size; // 小cluster在前
                        } else {
                            // size相同，按总total length排序
                            const aTotalLength = a.sortedNotebooks.reduce((sum, nb) => sum + nb.totalLines, 0);
                            const bTotalLength = b.sortedNotebooks.reduce((sum, nb) => sum + nb.totalLines, 0);
                            return aTotalLength - bTotalLength; // 总length小的在前
                        }
                    }
                });

                // 使用排序后的cluster顺序，cluster内部也按length排序
                clusterSizes.forEach(({ sortedNotebooks }) => {
                    sortedNotebooks.forEach(({ notebookIndex }) => {
                        this.notebookOrder.push(notebookIndex);
                    });
                });
            } else {
                // 使用原始cluster顺序
                clusterOrder.forEach(groupId => {
                    this.notebookOrder.push(...groupMap[groupId]);
                });
            }

            // 添加未分组的notebook
            this.notebookOrder.push(...ungroupedNotebooks);
        } else {
            this.notebookOrder = this.data.map((_, i) => i);
        }
        // 排序后派发事件
        const event = new CustomEvent('galaxy-notebook-order-changed', {
            detail: { notebookOrder: this.notebookOrder }
        });
        window.dispatchEvent(event);
        // 保存筛选状态
        this.saveFilterState();
    }

    onAfterAttach(): void {
        // 延迟恢复状态，确保tab切换完成
        setTimeout(() => {
            // 恢复状态
            this.restoreFilterState();
            this.updateNotebookOrder();

            // 绘制矩阵（restoreFilterState 中可能已经调用了 drawMatrix，所以这里检查一下）
            const existingContainer = this.node.querySelector('.matrix-container');
            if (!existingContainer) {
                this.drawMatrix();
            }

            // 更新cluster信息显示
            this.updateClusterInfo();
        }, 50); // 添加小延迟，确保tab切换完成

        window.addEventListener('galaxy-stage-hover', this.handleStageHover);
        window.addEventListener('galaxy-transition-hover', this.handleTransitionHover);
    }

    onBeforeDetach(): void {
        window.removeEventListener('galaxy-stage-hover', this.handleStageHover);
        window.removeEventListener('galaxy-transition-hover', this.handleTransitionHover);

        // 清理按钮的事件监听器
        const clearBtn = this.clusterInfoContainer?.querySelector('#clear-cluster-selection-btn') as HTMLButtonElement;
        if (clearBtn) {
            clearBtn.removeEventListener('click', this.clearClusterSelection);
        }
    }



    private handleStageHover = (event: Event) => {
        const detail = (event as CustomEvent).detail || {};
        const stage = detail.stage;
        const incomingTabId = detail.tabId;
        // Ignore hover events from non-overview tabs when tabId is provided
        if (incomingTabId && incomingTabId !== this.getTabId()) {
            return;
        }

        // 优化：使用防抖来减少频繁的DOM操作
        if (this.stageHoverTimeout) {
            clearTimeout(this.stageHoverTimeout);
        }

        this.stageHoverTimeout = setTimeout(() => {
            this.applyStageHover(stage);
        }, 16); // 约60fps的刷新率
    }

    // 优化的stage hover应用方法
    private applyStageHover(stage: string | null) {
        // 批量操作：先清除所有高亮和暗淡效果
        d3.selectAll('.matrix-cell')
            .classed('matrix-highlight', false)
            .classed('matrix-dim', false);

        if (stage) {
            if (this.selectedClusterId) {
                // 选中了cluster时，只在cluster内部处理
                const clusterNotebooks = this.notebookOrder.filter(row => {
                    const nb = this.data[row];
                    return this.isNotebookInSelectedCluster(nb);
                });

                // 只对cluster内的cells应用暗淡效果
                const clusterSelector = clusterNotebooks.map(row =>
                    `.matrix-cell[data-row="${row}"]`
                ).join(',');

                if (clusterSelector) {
                    d3.selectAll(clusterSelector).classed('matrix-dim', true);
                }

                // 高亮cluster内匹配的cells
                const highlightSelector = clusterNotebooks.map(row =>
                    `.matrix-cell-${stage}[data-row="${row}"]`
                ).join(',');

                if (highlightSelector) {
                    d3.selectAll(highlightSelector)
                        .classed('matrix-highlight', true)
                        .classed('matrix-dim', false);
                }
            } else {
                // 没有选中cluster时，全局处理
                d3.selectAll('.matrix-cell').classed('matrix-dim', true);

                d3.selectAll(`.matrix-cell-${stage}`)
                    .classed('matrix-highlight', true)
                    .classed('matrix-dim', false);
            }
        }
    }

    // 应用flow高亮的辅助方法
    private applyFlowHighlight(from: string, to: string): void {
        // 优化：批量操作，先清除所有高亮和暗淡效果
        d3.selectAll('.matrix-cell')
            .classed('matrix-highlight', false)
            .classed('matrix-dim', false);

        // 收集所有需要高亮的cell选择器
        const highlightSelectors: string[] = [];
        const dimSelectors: string[] = [];

        // 遍历所有 notebook
        this.notebookOrder.forEach((row) => {
            const nb = this.data[row];

            // 如果有选中的cluster，只处理该cluster内的notebooks
            if (this.selectedClusterId && !this.isNotebookInSelectedCluster(nb)) {
                return; // 跳过不在选中cluster内的notebook
            }

            const sortedCells = nb.cells.sort((a, b) => a.cellId - b.cellId);

            // 过滤可见cells（与drawMatrix中的逻辑保持一致）
            const processedCells = sortedCells.filter(cell =>
                this.showMarkdown || cell.cellType !== 'markdown'
            );

            // 找到所有符合transition的cell对（在processedCells中查找）
            const transitionPairs: number[][] = [];
            for (let i = 0; i < processedCells.length; i++) {
                const currStage = String(processedCells[i]["1st-level label"] ?? "None");
                if (currStage === from) {
                    // 向后查找下一个to stage的cell
                    for (let j = i + 1; j < processedCells.length; j++) {
                        const nextStage = String(processedCells[j]["1st-level label"] ?? "None");
                        if (nextStage === to) {
                            transitionPairs.push([i, j]);
                            break; // 找到第一个匹配的就停止
                        } else if (nextStage !== "None") {
                            // 如果遇到其他stage，停止搜索
                            break;
                        }
                        // 继续搜索
                    }
                }
            }

            // 收集需要高亮的cell选择器
            transitionPairs.forEach(([fromIdx, toIdx]) => {
                // 向前找连续 from
                let i0 = fromIdx;
                while (i0 > 0 && String(processedCells[i0 - 1]["1st-level label"] ?? "None") === from) i0--;
                // 向后找连续 to
                let i1 = toIdx;
                while (i1 + 1 < processedCells.length && String(processedCells[i1 + 1]["1st-level label"] ?? "None") === to) i1++;

                // 收集 from 段的选择器
                for (let j = i0; j <= fromIdx; j++) {
                    highlightSelectors.push(`.matrix-cell[data-row="${row}"][data-index="${j}"]`);
                }
                // 收集 to 段的选择器
                for (let j = toIdx; j <= i1; j++) {
                    highlightSelectors.push(`.matrix-cell[data-row="${row}"][data-index="${j}"]`);
                }
            });

            // 收集需要暗淡的cell选择器（当前notebook的所有cells）
            if (this.selectedClusterId) {
                // 选中了cluster时，只收集当前notebook的cells
                for (let j = 0; j < processedCells.length; j++) {
                    dimSelectors.push(`.matrix-cell[data-row="${row}"][data-index="${j}"]`);
                }
            }
        });

        if (this.selectedClusterId) {
            // 选中了cluster时，只对cluster内的cells应用暗淡效果
            if (dimSelectors.length > 0) {
                const combinedDimSelector = dimSelectors.join(',');
                d3.selectAll(combinedDimSelector).classed('matrix-dim', true);
            }
        } else {
            // 没有选中cluster时，对所有cells应用暗淡效果
            d3.selectAll('.matrix-cell').classed('matrix-dim', true);
        }

        // 批量高亮所有收集到的cells
        if (highlightSelectors.length > 0) {
            const combinedSelector = highlightSelectors.join(',');
            d3.selectAll(combinedSelector)
                .classed('matrix-highlight', true)
                .classed('matrix-dim', false);
        }
    }

    private handleTransitionHover = (event: Event) => {
        const detail = (event as CustomEvent).detail || {};
        const { from, to } = detail;
        const incomingTabId = detail.tabId;
        // Ignore hover events from non-overview tabs when tabId is provided
        if (incomingTabId && incomingTabId !== this.getTabId()) {
            return;
        }

        // 优化：使用防抖来减少频繁的DOM操作
        if (this.transitionHoverTimeout) {
            clearTimeout(this.transitionHoverTimeout);
        }

        this.transitionHoverTimeout = setTimeout(() => {
            this.applyTransitionHover(from, to);
        }, 16); // 约60fps的刷新率
    }

    // 优化的transition hover应用方法
    private applyTransitionHover(from: string | null, to: string | null) {
        if (!from || !to) {
            // 清除所有高亮效果
            d3.selectAll('.matrix-cell')
                .classed('matrix-highlight', false)
                .classed('matrix-dim', false);
            // 注意：不清除cluster-dim类，因为它由cluster选择控制
        } else {
            this.applyFlowHighlight(from, to);
        }
    }

    private drawMatrix(): void {
        const notebooks = this.data;
        const color = this.colorScale;
        let notebookOrder = this.notebookOrder.length ? this.notebookOrder : notebooks.map((_, i) => i);
        // ====== FILTER BY DROPLISTS ======
        const assignmentFilter = (this as any)._assignmentFilter || '';
        const studentFilter = (this as any)._studentFilter || '';
        notebookOrder = notebookOrder.filter(idx => {
            const nb = notebooks[idx] as any;
            const matchAssignment = !assignmentFilter || nb.assignment === assignmentFilter;
            const matchStudent = !studentFilter || nb.student_id === studentFilter;
            return matchAssignment && matchStudent;
        });

        const baseCellHeight = 5;
        const cellWidth = 20;
        const rowPadding = 1;
        const notebookSpacing = 2; // Add space between notebooks

        // Calculate additional spacing for similarity groups
        let groupSpacing = 0;
        const groupGap = 20; // White space between groups
        if (this.sortState === 3 && this.similarityGroups && this.similarityGroups.length > 0) {
            // Count unique groups in the current notebook order (including ungrouped notebooks as a separate group)
            const uniqueGroups = new Set();
            let hasUngrouped = false;
            notebookOrder.forEach(idx => {
                const nb = notebooks[idx] as any;
                // 安全检查：确保kernelVersionId存在
                if (nb && nb.kernelVersionId) {
                    const kernelId = nb.kernelVersionId.toString();
                    const simRow = this.similarityGroups.find((row: any) => row.kernelVersionId === kernelId);
                    if (simRow && simRow.cluster_id) {
                        uniqueGroups.add(simRow.cluster_id);
                    } else {
                        hasUngrouped = true;
                    }
                } else {
                    hasUngrouped = true;
                }
            });
            // 计算组数：cluster组数 + 未分组组（如果有的话）
            const totalGroups = uniqueGroups.size + (hasUngrouped ? 1 : 0);
            groupSpacing = Math.max(0, totalGroups - 1) * groupGap;
        }

        const svgWidth = Math.max(1000, notebookOrder.length * (cellWidth + rowPadding + notebookSpacing) + groupSpacing + 100);

        // 计算动态高度
        let totalHeight = 0;
        const cellHeights: number[][] = [];
        const cellYPositions: number[][] = [];

        notebookOrder.forEach((row) => {
            const nb = notebooks[row];
            const sortedCells = nb.cells.sort((a, b) => a.cellId - b.cellId);
            const heights: number[] = [];
            const yPositions: number[] = [];
            let currentY = 0;

            // 直接使用原始cells
            const processedCells = sortedCells.filter(cell =>
                this.showMarkdown || cell.cellType !== 'markdown'
            );

            processedCells.forEach((cell, i) => {
                let cellHeight: number;
                if (this.cellHeightMode === 'fixed') {
                    cellHeight = baseCellHeight;
                } else {
                    // 动态高度：基于代码行数
                    const code = (cell as any).source ?? (cell as any).code ?? '';
                    const lineCount = code.split(/\r?\n/).length;
                    cellHeight = Math.max(3, Math.min(20, 3 + lineCount * 0.8));
                }
                heights.push(cellHeight);
                yPositions.push(currentY);
                currentY += cellHeight + 0; // 减少cell间距，从1改为0
            });

            cellHeights.push(heights);
            cellYPositions.push(yPositions);
            totalHeight = Math.max(totalHeight, currentY);
        });

        // 计算内容高度
        let contentHeight = totalHeight + 100;

        // 在cluster模式下为cluster标签和cluster信息区域添加额外空间
        if (this.sortState === 3 && this.similarityGroups && this.similarityGroups.length > 0) {
            contentHeight += 50; // 为cluster标签预留50px空间
            contentHeight += 20; // 为cluster信息区域预留20px空间
        }

        // 获取容器高度（如为0可用默认值）
        const minHeight = this.node.clientHeight || 400;
        const svgHeight = Math.max(contentHeight, minHeight);

        // 先移除已有 matrix 容器，避免重复
        const old = this.node.querySelector('.matrix-container');
        if (old) old.remove();

        const container = document.createElement('div');
        container.className = 'matrix-container';
        container.style.flex = '1 1 auto';
        container.style.overflow = 'auto';
        container.style.height = 'auto';
        container.style.padding = '0px 8px 4px 8px';

        // 添加滚动事件监听器来保存滚动位置
        container.addEventListener('scroll', () => {
            this.saveFilterState();
        });

        this.node.appendChild(container);

        const svg = d3
            .select(container)
            .append('svg')
            .attr('width', svgWidth)
            .attr('height', svgHeight)
            .attr('id', 'matrix');

        // 在cluster模式下调整transform，为cluster标签和cluster信息区域留出空间
        const translateY = (this.sortState === 3 && this.similarityGroups && this.similarityGroups.length > 0) ? 60 : 30;
        const g = svg.append('g').attr('transform', `translate(20, ${translateY})`);

        const self = this;

        // Calculate column positions with group spacing
        const columnPositions: number[] = [];
        let currentX = 0;
        let prevGroupId: string | null = null;

        notebookOrder.forEach((row, colIdx) => {
            const nb = notebooks[row] as any;

            // Check if we need to add group spacing
            if (this.sortState === 3 && this.similarityGroups && this.similarityGroups.length > 0) {
                const kernelId = nb && nb.kernelVersionId ? nb.kernelVersionId.toString() : null;
                const simRow = kernelId ? this.similarityGroups.find((simRow: any) => simRow.kernelVersionId === kernelId) : null;
                const currentGroupId = simRow ? simRow.cluster_id : null;

                // Add spacing if this is a new group (but not for the first group)
                if (prevGroupId !== null && currentGroupId !== prevGroupId) {
                    currentX += groupGap;
                }
                prevGroupId = currentGroupId;
            }

            columnPositions.push(currentX);
            currentX += cellWidth + rowPadding + notebookSpacing;
        });

        notebookOrder.forEach((row, colIdx) => {
            const nb = notebooks[row];
            const sortedCells = nb.cells.sort((a, b) => a.cellId - b.cellId);

            let prevStage: string | null = null;
            let visibleCellIndex = 0; // 用于跟踪可见cell的索引

            // 检查当前notebook是否属于选中的cluster
            let isInSelectedCluster = false;
            if (this.selectedClusterId && this.sortState === 3 && this.similarityGroups && this.similarityGroups.length > 0) {
                const kernelId = (nb as any)?.kernelVersionId?.toString();
                const simRow = kernelId ? this.similarityGroups.find((row: any) => row.kernelVersionId === kernelId) : null;
                isInSelectedCluster = simRow && simRow.cluster_id === this.selectedClusterId;
            }

            // 直接使用原始cells
            const processedCells = sortedCells.filter(cell =>
                this.showMarkdown || cell.cellType !== 'markdown'
            );

            // 创建从processedCells索引到原始cells索引的映射
            const processedToOriginalIndexMap: number[] = [];
            sortedCells.forEach((cell, originalIndex) => {
                if (this.showMarkdown || cell.cellType !== 'markdown') {
                    processedToOriginalIndexMap.push(originalIndex);
                }
            });

            processedCells.forEach((cell, i) => {
                const currStage = String(cell["1st-level label"] ?? "None");
                const currClass = currStage;

                let transitionClass = "";
                if (prevStage) {
                    transitionClass = `pair-from-${prevStage}-to-${currClass}`;
                }

                const cellHeight = cellHeights[colIdx][visibleCellIndex];
                const cellY = cellYPositions[colIdx][visibleCellIndex];

                // 根据cluster选择状态决定cell的样式
                let cellFill = cell.cellType === 'code' ? color(currStage) : 'white';
                let cellStroke = cell.cellType === 'code' ? color(currStage) : '#bbb';

                // 在cluster模式下给cell添加额外的y偏移，避免与label重叠
                const cellYOffset = (this.sortState === 3 && this.similarityGroups && this.similarityGroups.length > 0) ? 20 : 0;

                const base = g
                    .append('rect')
                    .datum({ ...cell, kernelVersionId: (nb as any)?.kernelVersionId || null, notebook_name: (nb as any)?.notebook_name || null })
                    .attr('x', columnPositions[colIdx] + 0)
                    .attr('y', cellY + cellYOffset)
                    .attr('width', cellWidth - 2)
                    .attr('height', cellHeight - 2)
                    .attr('fill', cellFill)
                    .attr('stroke', cellStroke)
                    .attr('stroke-width', 1)
                    .attr('data-row', row.toString())
                    .attr('data-index', i.toString())
                    .attr('data-stage', currClass)
                    .attr('class', `matrix-cell matrix-cell-${currClass} ${transitionClass}`);

                // 根据cluster选择状态应用初始样式
                if (this.selectedClusterId && !isInSelectedCluster) {
                    // 如果选中了cluster但当前notebook不属于该cluster，则灰掉
                    base.attr('opacity', 0.3).classed('cluster-dim', true);
                }

                base.on('mouseover', function (event, d) {
                    // 立即应用高亮效果，避免延迟
                    d3.select(this)
                        .classed('matrix-highlight', true)
                        .classed('matrix-dim', false)
                        .attr('stroke', d.cellType === 'code' ? color(String(d["1st-level label"] ?? "None")) : '#bbb')
                        .attr('filter', 'drop-shadow(0px 0px 6px rgba(0,0,0,0.18))');

                    // 高亮对应的notebook
                    const notebookIndex = nb?.globalIndex;
                    if (notebookIndex) {
                        window.dispatchEvent(new CustomEvent('galaxy-notebook-highlight', {
                            detail: {
                                notebookIndex: notebookIndex,
                                highlight: true
                            }
                        }));
                    }

                    // 使用缓存的tooltip元素或创建新的
                    let tooltip = (window as any)._galaxyTooltip;
                    if (!tooltip) {
                        tooltip = document.createElement('div');
                        tooltip.id = 'galaxy-tooltip';
                        tooltip.style.position = 'fixed';
                        tooltip.style.display = 'none';
                        tooltip.style.pointerEvents = 'none';
                        tooltip.style.background = 'rgba(0,0,0,0.75)';
                        tooltip.style.color = '#fff';
                        tooltip.style.padding = '6px 10px';
                        tooltip.style.borderRadius = '4px';
                        tooltip.style.fontSize = '12px';
                        tooltip.style.zIndex = '9999';
                        document.body.appendChild(tooltip);
                        (window as any)._galaxyTooltip = tooltip;
                    }

                    // 预计算tooltip内容
                    const code = (d as any).source ?? (d as any).code ?? '';
                    const lineCount = code.split(/\r?\n/).length;
                    const kernelId = (d as any)?.kernelVersionId?.toString();
                    const titleFromMap = kernelId ? self.kernelTitleMap.get(kernelId) : null;
                    const notebookTitle = titleFromMap?.title || kernelId || 'Unknown';

                    let tooltipContent = `Stage: ${typeof LABEL_MAP !== 'undefined' ? (LABEL_MAP[String(d["1st-level label"] ?? "None")] ?? d["1st-level label"] ?? "None") : (d["1st-level label"] ?? "None")}` +
                        `<br>Title: ${notebookTitle}` +
                        `<br>Lines: ${lineCount}`;

                    // 添加投票信息
                    if (self.voteData && self.voteData.length > 0) {
                        const voteRow = kernelId ? self.voteData.find((row: any) => row.kernelVersionId === kernelId) : null;
                        if (voteRow && voteRow.TotalVotes !== undefined) {
                            tooltipContent += `<br>Votes: ${voteRow.TotalVotes}`;
                        }
                    }

                    // 如果有 similarityGroups，显示 similarity, label_integers
                    if (self.similarityGroups && self.similarityGroups.length > 0) {
                        const simRow = kernelId ? self.similarityGroups.find((row: any) => row.kernelVersionId === kernelId) : null;
                        if (simRow && simRow.similarity !== undefined) {
                            tooltipContent += `<br>similarity: ${simRow.similarity}`;
                        }
                    }

                    // 一次性设置tooltip内容和位置
                    tooltip.innerHTML = tooltipContent;
                    tooltip.style.left = event.clientX + 12 + 'px';
                    tooltip.style.top = event.clientY + 12 + 'px';
                    tooltip.style.display = 'block';
                })
                    .on('mousemove', function (event) {
                        const tooltip = (window as any)._galaxyTooltip;
                        if (tooltip && tooltip.style.display === 'block') {
                            tooltip.style.left = event.clientX + 12 + 'px';
                            tooltip.style.top = event.clientY + 12 + 'px';
                        }
                    })
                    .on('mouseout', function (event, d) {
                        d3.select(this).classed('matrix-highlight', false)
                            .attr('filter', null);
                        const datum = d3.select(this).datum() as Cell;
                        if (datum.cellType !== 'code') {
                            d3.select(this).attr('stroke', '#bbb');
                        } else {
                            d3.select(this).attr('stroke', color(String(datum["1st-level label"] ?? "None")));
                        }

                        // 取消notebook高亮
                        const notebookIndex = nb?.globalIndex;
                        if (notebookIndex) {
                            window.dispatchEvent(new CustomEvent('galaxy-notebook-highlight', {
                                detail: {
                                    notebookIndex: notebookIndex,
                                    highlight: false
                                }
                            }));
                        }

                        const tooltip = (window as any)._galaxyTooltip;
                        if (tooltip) {
                            tooltip.style.display = 'none';
                        }

                        // 由于matrix不再跟随notebook detail tab的选择，这里不再恢复高亮状态
                    })
                    .on('click', function (event, d) {
                        // Track matrix cell click
                        analytics.trackMatrixInteraction('cell_click', {
                            cellType: d.cellType,
                            stageLabel: d["1st-level label"],
                            notebookIndex: nb.globalIndex,
                            cellIndex: i,
                            kernelVersionId: (nb as any).kernelVersionId,
                            notebookName: (nb as any).notebook_name,
                            interaction_context: 'cell_navigation'
                        });

                        // 派发 notebook 跳转和 cell 详情事件
                        // 先隐藏 tooltip
                        const tooltip = document.getElementById('galaxy-tooltip');
                        if (tooltip) tooltip.style.display = 'none';
                        const notebookObj = { ...nb, index: nb.globalIndex };
                        window.dispatchEvent(new CustomEvent('galaxy-notebook-selected', {
                            detail: { notebook: notebookObj }
                        }));
                        setTimeout(() => {
                            // 如果是markdown cell，只跳转到notebook，不显示cell detail
                            if (d.cellType === 'markdown') {
                                // 不触发cell detail事件，让DetailSidebar显示notebook概览
                            } else {
                                // 对于code cell，显示cell detail
                                // 使用映射将processedCells的索引转换为原始cells的索引
                                const originalCellIndex = processedToOriginalIndexMap[i];
                                window.dispatchEvent(new CustomEvent('galaxy-notebook-detail-jump', {
                                    detail: {
                                        notebookIndex: nb.globalIndex,
                                        cellIndex: originalCellIndex,
                                        kernelVersionId: (nb as any).kernelVersionId
                                    }
                                }));
                                window.dispatchEvent(new CustomEvent('galaxy-cell-detail', {
                                    detail: {
                                        cell: { ...d, notebookIndex: nb.globalIndex, cellIndex: originalCellIndex, _notebookDetail: notebookObj }
                                    }
                                }));

                                // Track cell detail opened from matrix
                                analytics.trackCellDetailOpened({
                                    cellType: d.cellType,
                                    cellIndex: originalCellIndex,
                                    notebookIndex: nb.globalIndex,
                                    notebookId: `Notebook ${nb.globalIndex}`,
                                    notebookName: (nb as any).notebook_name,
                                    kernelVersionId: (nb as any).kernelVersionId,
                                    stageLabel: d["1st-level label"],
                                    source: 'matrix'
                                });
                            }
                        }, 0);
                    });

                if (prevStage) {
                    d3.select(base.node()?.previousSibling as SVGRectElement).classed(transitionClass, true);
                }
                prevStage = currStage;
                visibleCellIndex++; // Increment visibleCellIndex after each cell
            });
        });

        // 添加列编号
        const headerG = g.append('g').attr('class', 'matrix-header');
        // 在cluster模式下给notebook label添加额外的y偏移，避免与cluster label重叠
        // const labelYOffset = (this.sortState === 3 && this.similarityGroups && this.similarityGroups.length > 0) ? 15 : 0;

        for (let col = 0; col < notebookOrder.length; col++) {
            const nb = notebooks[notebookOrder[col]];
            headerG.append('text')
                .attr('x', columnPositions[col] + cellWidth / 2)
                .attr('y', (this.sortState === 3 && this.similarityGroups && this.similarityGroups.length > 0) ? 13 : -8)
                .attr('text-anchor', 'middle')
                .attr('font-size', '10px')
                .attr('fill', '#555')
                .style('cursor', 'pointer')
                .text(nb?.globalIndex ?? (col + 1))
                .on('mouseover', function () {
                    // 高亮对应的notebook
                    const notebookIndex = nb?.globalIndex;
                    if (notebookIndex) {
                        window.dispatchEvent(new CustomEvent('galaxy-notebook-highlight', {
                            detail: {
                                notebookIndex: notebookIndex,
                                highlight: true
                            }
                        }));
                    }
                })
                .on('mouseout', function () {
                    // 取消notebook高亮
                    const notebookIndex = nb?.globalIndex;
                    if (notebookIndex) {
                        window.dispatchEvent(new CustomEvent('galaxy-notebook-highlight', {
                            detail: {
                                notebookIndex: notebookIndex,
                                highlight: false
                            }
                        }));
                    }
                })
                .on('click', () => {
                    window.dispatchEvent(new CustomEvent('galaxy-notebook-selected', { detail: { notebook: { ...nb, index: nb?.globalIndex ?? 0 } } }));
                });
        }

        // 在cluster模式下添加cluster标签
        if (this.sortState === 3 && this.similarityGroups && this.similarityGroups.length > 0) {
            const clusterLabelsG = g.append('g').attr('class', 'cluster-labels');

            // 计算每个cluster的范围
            const clusterRanges: { clusterId: string; startCol: number; endCol: number; startX: number; endX: number }[] = [];
            let currentClusterId: string | null = null;
            let clusterStartCol = 0;
            let clusterStartX = columnPositions[0];

            for (let col = 0; col < notebookOrder.length; col++) {
                const nb = notebooks[notebookOrder[col]] as any;
                const kernelId = nb && nb.kernelVersionId ? nb.kernelVersionId.toString() : null;
                const simRow = kernelId ? this.similarityGroups.find((row: any) => row.kernelVersionId === kernelId) : null;
                const clusterId = simRow ? simRow.cluster_id : null;

                // 如果cluster ID发生变化，保存前一个cluster的范围
                if (clusterId !== currentClusterId) {
                    if (currentClusterId !== null) {
                        const endX = columnPositions[col - 1] + cellWidth;
                        clusterRanges.push({
                            clusterId: currentClusterId,
                            startCol: clusterStartCol,
                            endCol: col - 1,
                            startX: clusterStartX,
                            endX: endX
                        });
                    }

                    // 开始新的cluster
                    currentClusterId = clusterId;
                    clusterStartCol = col;
                    clusterStartX = columnPositions[col];
                }
            }

            // 添加最后一个cluster的范围
            if (currentClusterId !== null) {
                const endX = columnPositions[notebookOrder.length - 1] + cellWidth;
                clusterRanges.push({
                    clusterId: currentClusterId,
                    startCol: clusterStartCol,
                    endCol: notebookOrder.length - 1,
                    startX: clusterStartX,
                    endX: endX
                });
            }

            // 为每个cluster绘制标签
            clusterRanges.forEach((range, index) => {
                const centerX = (range.startX + range.endX) / 2;
                const isSelected = this.selectedClusterId === range.clusterId;

                // 绘制横线
                clusterLabelsG.append('line')
                    .attr('x1', range.startX)
                    .attr('y1', -5)
                    .attr('x2', range.endX)
                    .attr('y2', -5)
                    .attr('stroke', isSelected ? '#4caf50' : '#666')
                    .attr('stroke-width', isSelected ? 3 : 2)
                    .attr('stroke-linecap', 'round')
                    .attr('data-cluster-id', range.clusterId)
                    .style('cursor', 'pointer')
                    .on('click', () => {
                        this.selectCluster(range.clusterId);
                    });

                // 绘制cluster标签文本
                clusterLabelsG.append('text')
                    .attr('x', centerX)
                    .attr('y', -30)
                    .attr('text-anchor', 'middle')
                    .attr('font-size', '11px')
                    .attr('font-weight', '600')
                    .attr('fill', isSelected ? '#4caf50' : '#333')
                    .attr('data-cluster-id', range.clusterId)
                    .style('cursor', 'pointer')
                    .text(`Cluster ${range.clusterId}`)
                    .on('click', () => {
                        this.selectCluster(range.clusterId);
                    });

                // 添加数量信息
                const notebookCount = range.endCol - range.startCol + 1;
                clusterLabelsG.append('text')
                    .attr('x', centerX)
                    .attr('y', -18)
                    .attr('text-anchor', 'middle')
                    .attr('font-size', '9px')
                    .attr('font-weight', '400')
                    .attr('fill', isSelected ? '#4caf50' : '#666')
                    .attr('data-cluster-id', range.clusterId)
                    .style('cursor', 'pointer')
                    .text(`${notebookCount} notebook${notebookCount !== 1 ? 's' : ''}`)
                    .on('click', () => {
                        this.selectCluster(range.clusterId);
                    });

                // // 添加垂直线连接到横线
                // clusterLabelsG.append('line')
                //     .attr('x1', centerX)
                //     .attr('y1', -35)
                //     .attr('x2', centerX)
                //     .attr('y2', -25)
                //     .attr('stroke', isSelected ? '#4caf50' : '#666')
                //     .attr('stroke-width', 1);
            });
        }

        // 在矩阵绘制完成后恢复滚动位置和更新cluster信息
        setTimeout(() => {
            this.restoreScrollPosition();
            this.updateClusterInfo();
        }, 200); // 增加延迟时间，确保容器完全渲染
    }

    // 恢复滚动位置
    private restoreScrollPosition(): void {
        const tabId = this.getTabId();
        const stateKey = `_galaxyMatrixFilterState_${tabId}`;
        const savedState = (window as any)[stateKey];

        if (savedState && (savedState.scrollLeft !== undefined || savedState.scrollTop !== undefined)) {
            const matrixContainer = this.node.querySelector('.matrix-container') as HTMLElement;
            if (matrixContainer) {
                // 使用更可靠的方式来检测容器是否准备好
                const isContainerReady = () => {
                    const svg = matrixContainer.querySelector('svg');
                    const hasContent = svg && svg.children.length > 0;
                    const hasScrollableContent = matrixContainer.scrollWidth > matrixContainer.clientWidth ||
                        matrixContainer.scrollHeight > matrixContainer.clientHeight;
                    return hasContent && hasScrollableContent;
                };

                const restoreScroll = () => {
                    if (isContainerReady()) {
                        matrixContainer.scrollLeft = savedState.scrollLeft || 0;
                        matrixContainer.scrollTop = savedState.scrollTop || 0;
                        return true; // 成功恢复
                    } else {
                        return false; // 需要重试
                    }
                };

                // 使用递归重试机制，最多重试10次，每次间隔递增
                let retryCount = 0;
                const maxRetries = 10;

                const attemptRestore = () => {
                    if (retryCount >= maxRetries) {
                        return;
                    }

                    if (!restoreScroll()) {
                        retryCount++;
                        const delay = Math.min(100 * retryCount, 1000); // 递增延迟，最大1秒
                        setTimeout(attemptRestore, delay);
                    }
                };

                // 开始尝试恢复
                requestAnimationFrame(attemptRestore);
            }
        }
    }

    getNotebookOrder(): number[] {
        return this.notebookOrder;
    }

    // 重置MatrixWidget状态，用于切换competition时
    resetState(): void {
        // 默认使用非cluster模式（原始顺序）
        this.sortState = 0;
        this.voteEnabled = false;
        this.lengthSortEnabled = true; // 非cluster模式下默认启用length排序
        this.clusterSizeSortDirection = 'asc'; // 默认升序
        this.notebookOrder = this.data.map((_, i) => i);
        (this as any)._assignmentFilter = '';
        (this as any)._studentFilter = '';
        this.cellHeightMode = 'fixed';
        this.showMarkdown = false; // 默认不显示markdown
        this.selectedClusterId = null; // 重置cluster选择状态
        // 注意：competitionInfo不需要重置，因为它由构造函数设置

        // 只有在DOM元素已经创建时才更新按钮状态
        if (this.sortButton) {
            this.sortButton.innerHTML = this.getSortIcon();
        }
        if (this.similaritySortButton) {
            this.similaritySortButton.innerHTML = this.getSimilaritySortIcon();
            // 默认不激活cluster按钮
            this.similaritySortButton.classList.remove('active');
        }
        if (this.cellHeightButton) {
            this.cellHeightButton.innerHTML = this.getCellHeightIcon();
        }
        if (this.markdownButton) {
            this.markdownButton.innerHTML = this.getMarkdownIcon();
        }
        if (this.voteSortButton) {
            this.voteSortButton.innerHTML = this.getVoteSortIcon();
            this.voteSortButton.classList.remove('active');
        }
        this.updateSortButtonState();

        // 应用排序
        this.updateNotebookOrder();

        // 只有在DOM元素已经创建时才重置筛选器
        if (this.node) {
            const assignmentSelect = this.node.querySelector('select') as HTMLSelectElement;
            const studentSelect = this.node.querySelectorAll('select')[1] as HTMLSelectElement;
            if (assignmentSelect) assignmentSelect.value = '';
            if (studentSelect) studentSelect.value = '';
        }

        // 清除保存的状态
        const tabId = this.getTabId();
        const stateKey = `_galaxyMatrixFilterState_${tabId}`;
        delete (window as any)[stateKey];

        // 更新cluster信息显示
        this.updateClusterInfo();
    }

    setFilter(selection: any) {
        // 移除对filter的响应，让matrix不再跟随notebook detail tab的选择
        // 这个方法现在不做任何事情
    }

    // 获取当前筛选后的notebook列表
    private getFilteredNotebooks(): any[] {
        const assignmentFilter = (this as any)._assignmentFilter || '';
        const studentFilter = (this as any)._studentFilter || '';
        return this.data.filter(nb => {
            const matchAssignment = !assignmentFilter || (nb as any).assignment === assignmentFilter;
            const matchStudent = !studentFilter || (nb as any).student_id === studentFilter;
            return matchAssignment && matchStudent;
        });
    }

    // 获取基于cluster筛选的notebook列表
    private getClusterFilteredNotebooks(): any[] {
        const baseFilteredNotebooks = this.getFilteredNotebooks();

        // 如果没有选中cluster，返回基础筛选结果
        if (!this.selectedClusterId) {
            return baseFilteredNotebooks;
        }

        // 如果选中了cluster，只返回属于该cluster的notebook
        return baseFilteredNotebooks.filter(nb => {
            const kernelId = (nb as any).kernelVersionId?.toString();
            const simRow = kernelId ? this.similarityGroups.find((row: any) => row.kernelVersionId === kernelId) : null;
            return simRow && simRow.cluster_id === this.selectedClusterId;
        });
    }

    // 根据当前排序状态更新按钮样式和可用性
    private updateSortButtonState() {
        if (this.sortButton) {
            this.sortButton.style.opacity = '1';
            this.sortButton.style.cursor = 'pointer';
            this.sortButton.disabled = false;
        }
    }

    // 获取当前tab ID
    private getTabId(): string {
        return 'overview';
    }

    // 保存筛选状态到全局变量（按tab隔离）
    private saveFilterState() {
        const tabId = this.getTabId();
        const stateKey = `_galaxyMatrixFilterState_${tabId}`;

        // 获取之前保存的状态
        const previousState = (window as any)[stateKey];

        // 保存当前滚动位置
        const matrixContainer = this.node.querySelector('.matrix-container') as HTMLElement;
        const scrollLeft = matrixContainer ? matrixContainer.scrollLeft : 0;
        const scrollTop = matrixContainer ? matrixContainer.scrollTop : 0;

        // 如果当前滚动位置为0，但之前有有效的滚动位置，则保留之前的滚动位置
        const finalScrollLeft = (scrollLeft === 0 && previousState && previousState.scrollLeft > 0) ? previousState.scrollLeft : scrollLeft;
        const finalScrollTop = (scrollTop === 0 && previousState && previousState.scrollTop > 0) ? previousState.scrollTop : scrollTop;

        (window as any)[stateKey] = {
            sortState: this.sortState,
            voteEnabled: this.voteEnabled,
            lengthSortEnabled: this.lengthSortEnabled,
            clusterSizeSortDirection: this.clusterSizeSortDirection,
            notebookOrder: this.notebookOrder,
            assignmentFilter: (this as any)._assignmentFilter,
            studentFilter: (this as any)._studentFilter,
            cellHeightMode: this.cellHeightMode,
            showMarkdown: this.showMarkdown,
            selectedClusterId: this.selectedClusterId,
            competitionInfo: this.competitionInfo, // 保存competition信息
            scrollLeft: finalScrollLeft,
            scrollTop: finalScrollTop
        };
    }

    // 隐藏所有tooltip
    private hideAllTooltips() {
        // 隐藏galaxy-tooltip
        const galaxyTooltip = (window as any)._galaxyTooltip;
        if (galaxyTooltip) {
            galaxyTooltip.style.opacity = '0';
            setTimeout(() => {
                if (galaxyTooltip && galaxyTooltip.style.opacity === '0') {
                    galaxyTooltip.style.display = 'none';
                }
            }, 200);
        }
        // 隐藏tooltip
        const tooltip = document.getElementById('tooltip');
        if (tooltip) {
            tooltip.style.opacity = '0';
        }
    }

    // 重新创建tooltip
    private recreateTooltip() {
        // 清除现有的tooltip
        const existingTooltip = (window as any)._galaxyTooltip;
        if (existingTooltip) {
            existingTooltip.remove();
            (window as any)._galaxyTooltip = null;
        }

        // 创建新的tooltip元素
        const tooltip = document.createElement('div');
        tooltip.id = 'galaxy-tooltip';
        tooltip.style.position = 'fixed';
        tooltip.style.display = 'none';
        tooltip.style.pointerEvents = 'none';
        tooltip.style.background = 'rgba(0,0,0,0.75)';
        tooltip.style.color = '#fff';
        tooltip.style.padding = '6px 10px';
        tooltip.style.borderRadius = '4px';
        tooltip.style.fontSize = '12px';
        tooltip.style.zIndex = '9999';
        document.body.appendChild(tooltip);
        (window as any)._galaxyTooltip = tooltip;
    }

    // 从全局变量恢复筛选状态（按tab隔离）
    private restoreFilterState() {
        // 切换tab时隐藏所有tooltip
        this.hideAllTooltips();

        const tabId = this.getTabId();
        const stateKey = `_galaxyMatrixFilterState_${tabId}`;
        const savedState = (window as any)[stateKey];

        if (savedState) {
            this.sortState = savedState.sortState;
            this.voteEnabled = savedState.voteEnabled || false;
            this.lengthSortEnabled = savedState.lengthSortEnabled !== undefined ? savedState.lengthSortEnabled : true;
            this.clusterSizeSortDirection = savedState.clusterSizeSortDirection || 'asc';
            this.notebookOrder = savedState.notebookOrder || this.data.map((_, i) => i);
            (this as any)._assignmentFilter = savedState.assignmentFilter || '';
            (this as any)._studentFilter = savedState.studentFilter || '';
            this.cellHeightMode = savedState.cellHeightMode || 'fixed';
            this.showMarkdown = savedState.showMarkdown !== undefined ? savedState.showMarkdown : false; // 恢复markdown显示状态
            this.selectedClusterId = savedState.selectedClusterId || null; // 恢复cluster选择状态
            this.competitionInfo = savedState.competitionInfo || null; // 恢复competition信息

            // 更新按钮状态
            this.sortButton.innerHTML = this.getSortIcon();
            this.similaritySortButton.innerHTML = this.getSimilaritySortIcon();
            this.voteSortButton.innerHTML = this.getVoteSortIcon();
            this.cellHeightButton.innerHTML = this.getCellHeightIcon();
            this.markdownButton.innerHTML = this.getMarkdownIcon();

            // 恢复vote按钮的active状态
            if (this.voteEnabled) {
                this.voteSortButton.classList.add('active');
            } else {
                this.voteSortButton.classList.remove('active');
            }

            this.updateSortButtonState();

            // 更新cluster信息显示
            this.updateClusterInfo();

            // 恢复assignment和student筛选器的值
            const assignmentSelect = this.node.querySelector('select') as HTMLSelectElement;
            const studentSelect = this.node.querySelectorAll('select')[1] as HTMLSelectElement;
            if (assignmentSelect) assignmentSelect.value = (this as any)._assignmentFilter;
            if (studentSelect) studentSelect.value = (this as any)._studentFilter;

            // 只有在没有现有容器时才重新绘制矩阵
            const existingContainer = this.node.querySelector('.matrix-container');
            if (!existingContainer) {
                this.drawMatrix();
                // 在 drawMatrix 后延迟恢复滚动位置，给容器更多时间渲染
                setTimeout(() => {
                    this.restoreScrollPosition();
                    // 重新创建tooltip以确保它能正常工作
                    this.recreateTooltip();
                }, 200); // 增加延迟时间
            } else {
                // 如果容器已存在，也需要延迟恢复滚动位置，确保tab切换完成
                setTimeout(() => {
                    this.restoreScrollPosition();
                    // 重新创建tooltip以确保它能正常工作
                    this.recreateTooltip();
                }, 200); // 增加延迟时间
            }
        } else {
            // 如果没有保存的状态，使用默认状态
            // 默认使用非cluster模式（原始顺序）
            this.sortState = 0;
            this.voteEnabled = false;
            this.lengthSortEnabled = true; // 非cluster模式下默认启用length排序
            this.clusterSizeSortDirection = 'asc'; // 默认升序
            this.notebookOrder = this.data.map((_, i) => i);
            (this as any)._assignmentFilter = '';
            (this as any)._studentFilter = '';
            this.cellHeightMode = 'fixed';
            this.showMarkdown = false; // 默认不显示markdown
            this.selectedClusterId = null; // 重置cluster选择状态
            // competitionInfo保持构造函数设置的值，不需要重置

            // 更新按钮状态
            this.sortButton.innerHTML = this.getSortIcon();
            this.similaritySortButton.innerHTML = this.getSimilaritySortIcon();
            this.voteSortButton.innerHTML = this.getVoteSortIcon();
            this.cellHeightButton.innerHTML = this.getCellHeightIcon();
            this.markdownButton.innerHTML = this.getMarkdownIcon();

            // 重置vote按钮的active状态
            this.voteSortButton.classList.remove('active');
            // 默认不激活cluster按钮
            this.similaritySortButton.classList.remove('active');

            this.updateSortButtonState();

            // 更新cluster信息显示
            this.updateClusterInfo();

            // 应用默认排序
            this.updateNotebookOrder();

            // 重置筛选器
            const assignmentSelect = this.node.querySelector('select') as HTMLSelectElement;
            const studentSelect = this.node.querySelectorAll('select')[1] as HTMLSelectElement;
            if (assignmentSelect) assignmentSelect.value = '';
            if (studentSelect) studentSelect.value = '';

            // 只有在没有现有容器时才重新绘制矩阵
            const existingContainer = this.node.querySelector('.matrix-container');
            if (!existingContainer) {
                this.drawMatrix();
            }
        }
    }

    // 选择cluster
    private selectCluster(clusterId: string | null) {
        // 保存当前的stage或transition选中状态

        if (this.selectedClusterId === clusterId) {
            // 如果点击的是当前选中的cluster，则取消选择
            this.selectedClusterId = null;
        } else {
            // 选择新的cluster
            this.selectedClusterId = clusterId;
        }

        // 优化：只更新cell的透明度，而不是重新绘制整个矩阵
        this.updateCellOpacityForClusterSelection();

        // 更新cluster信息显示
        this.updateClusterInfo();

        // 由于matrix不再跟随notebook detail tab的选择，这里不再恢复高亮状态

        // Track cluster selection
        analytics.trackMatrixInteraction('cluster_selected', {
            clusterId: this.selectedClusterId,
            action: this.selectedClusterId ? 'select' : 'deselect',
            clusterSize: this.selectedClusterId ? this.getClusterFilteredNotebooks().length : 0,
            interaction_context: 'cluster_filtering'
        });

        // 派发cluster选择事件，通知LeftSidebar更新数据
        const clusterFilteredNotebooks = this.getClusterFilteredNotebooks();
        window.dispatchEvent(new CustomEvent('galaxy-cluster-selected', {
            detail: {
                clusterId: this.selectedClusterId,
                notebooks: clusterFilteredNotebooks
            }
        }));
    }

    // 更新cluster信息显示
    private updateClusterInfo() {
        if (!this.clusterInfoContainer) return;

        if (this.sortState === 3 && this.similarityGroups && this.similarityGroups.length > 0) {
            this.clusterInfoContainer.style.display = 'block';

            if (this.selectedClusterId) {
                // 显示选中cluster的详细信息
                this.showSelectedClusterInfo();
            } else {
                // 显示cluster概览信息
                this.showClusterOverview();
            }
        } else if (this.competitionInfo) {
            // 不聚类时显示competition信息
            this.clusterInfoContainer.style.display = 'block';
            this.showCompetitionInfo();
        } else {
            this.clusterInfoContainer.style.display = 'none';
        }
    }

    // 显示选中cluster的详细信息
    private showSelectedClusterInfo() {
        if (!this.clusterInfoContainer || !this.selectedClusterId) return;

        // 获取选中cluster的notebook
        const clusterNotebooks = this.data.filter((nb, index) => {
            const kernelId = (nb as any).kernelVersionId?.toString();
            const simRow = kernelId ? this.similarityGroups.find((row: any) => row.kernelVersionId === kernelId) : null;
            return simRow && simRow.cluster_id === this.selectedClusterId;
        });

        // 从summaryData中获取cluster的title和description
        let clusterTitle = this.getClusterTitle(this.selectedClusterId);
        // 在title前面加上cluster序号
        clusterTitle = `Cluster ${this.selectedClusterId}: ${clusterTitle}`;
        let clusterDescription = '';

        if (this.summaryData && this.summaryData.analysis_sections) {
            // 查找individual_summaries中的structured内容
            if (this.summaryData.analysis_sections.individual_summaries &&
                this.summaryData.analysis_sections.individual_summaries.structured) {
                const individualSummaries = this.summaryData.analysis_sections.individual_summaries.structured;
                const description = individualSummaries[this.selectedClusterId];
                if (description) {
                    clusterDescription = description;
                    console.log('Found description for cluster', this.selectedClusterId, ':', description);
                } else {
                    console.log('No description found for cluster', this.selectedClusterId);
                }
            }
        }

        // 计算cluster统计信息
        const totalNotebooks = clusterNotebooks.length;
        const totalCells = clusterNotebooks.reduce((sum, nb) => sum + nb.cells.length, 0);
        const avgCells = totalNotebooks > 0 ? Math.round(totalCells / totalNotebooks) : 0;

        // 计算code lines统计 - 使用totalLines属性
        let totalCodeLines = 0;
        clusterNotebooks.forEach(nb => {
            // 使用totalLines属性获取代码行数
            const notebookTotalLines = (nb as any).totalLines || 0;
            totalCodeLines += notebookTotalLines;
        });

        const avgCodeLines = totalNotebooks > 0 ? Math.round(totalCodeLines / totalNotebooks) : 0;

        // 使用从LeftSidebar传来的top stages和top transitions
        const { topStages, topTransitions } = this.topStats;

        // 获取投票信息
        let totalVotes = 0;
        let avgVotes = 0;
        if (this.voteData && this.voteData.length > 0) {
            const clusterVotes = clusterNotebooks.map(nb => {
                const kernelId = (nb as any).kernelVersionId?.toString();
                const voteRow = kernelId ? this.voteData.find((row: any) => row.kernelVersionId === kernelId) : null;
                return voteRow ? parseFloat(voteRow.TotalVotes) || 0 : 0;
            });
            totalVotes = clusterVotes.reduce((sum, votes) => sum + votes, 0);
            avgVotes = clusterVotes.length > 0 ? Math.round(totalVotes / clusterVotes.length) : 0;
        }

        this.clusterInfoContainer.innerHTML = `
            <div style="font-size:16px; font-weight:700; margin-bottom:12px; line-height:1.3; padding-bottom:8px; border-bottom:1px solid #e9ecef; display:flex; justify-content:space-between; align-items:flex-start; gap:12px;">
                <div style="display:flex; flex-direction:column; gap:4px; flex:1; min-width:0;">
                    <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                        <span id="cluster-title-btn" style="color: #4caf50; word-break:break-word; line-height:1.4; text-decoration: underline; cursor: pointer;">${clusterTitle}</span>
                        <span style="color: #6c757d; font-size: 13px; font-weight: 400; white-space:nowrap;display:none;">
                            ${totalNotebooks} notebooks
                        </span>
                    </div>
                </div>
                <div style="display:flex; gap:8px; flex-shrink:0;">
                    <button id="clear-cluster-selection-btn" 
                            style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 6px 12px; cursor: pointer; font-size: 12px; color: #6c757d; transition: background-color 0.2s; font-weight: 500; white-space:nowrap;">
                        ✕ Clear Selection
                    </button>
                </div>
            </div>
            
            <div style="display:flex; gap:16px; align-items:flex-start;">
                <!-- 左边：Description + Statistics -->
                <div style="flex: 1; min-width: 0; display: flex; flex-direction: column;">
                    ${clusterDescription ? `
                        <div style="margin-bottom:8px;">
                            <div style="font-size:14px; font-weight:600; margin-bottom:6px; color:#222; display:flex; align-items:center; gap:6px;">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="#666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                    <polyline points="14,2 14,8 20,8" stroke="#666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                    <line x1="16" y1="13" x2="8" y2="13" stroke="#666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                    <line x1="16" y1="17" x2="8" y2="17" stroke="#666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                    <polyline points="10,9 9,9 8,9" stroke="#666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                </svg>
                                Summary
                            </div>
                            <div style="background:#fff; border-radius:6px; padding:12px; border:1px solid #e9ecef; box-shadow:0 1px 3px rgba(0,0,0,0.05); height: 70px; overflow-y: auto;">
                                <div style="font-size:13px; color:#222; line-height:1.5; font-weight:400;">${clusterDescription}</div>
                            </div>
                        </div>
                    ` : ''}
                    
                    <div style="flex: 1; display: none; flex-direction: column; justify-content: flex-end;">
                        <div style="font-size:14px; font-weight:600; margin-bottom:6px; color:#222; display:flex; align-items:center; gap:6px;">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M3 3v18h18" stroke="#666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M18 17V9" stroke="#666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M13 17V5" stroke="#666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M8 17v-3" stroke="#666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                            Statistics
                        </div>
                        <div style="background:#fff; border-radius:6px; padding:12px; border:1px solid #e9ecef; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                            <div style="display:flex; flex-direction:row; gap:12px;">
                                <div style="flex:1; display:flex; flex-direction:column; justify-content:flex-end;">
                                    <div style="font-size:11px; color:#6c757d; margin-bottom:2px;">Avg Cells/Notebook</div>
                                    <div style="font-size:13px; font-weight:600; color:#495057;">${avgCells.toLocaleString()}</div>
                                </div>
                                <div style="flex:1; display:flex; flex-direction:column; justify-content:flex-end;">
                                    <div style="font-size:11px; color:#6c757d; margin-bottom:2px;">Avg Code Lines/Notebook</div>
                                    <div style="font-size:13px; font-weight:600; color:#495057;">${avgCodeLines.toLocaleString()}</div>
                                </div>
                                ${this.voteData && this.voteData.length > 0 ? `
                                    <div style="flex:1; display:flex; flex-direction:column; justify-content:flex-end;">
                                        <div style="font-size:11px; color:#6c757d; margin-bottom:2px;">Avg Votes/Notebook</div>
                                        <div style="font-size:13px; font-weight:600; color:#495057;">${avgVotes.toLocaleString()}</div>
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 右边：Top Patterns -->
                <div style="flex: 1; min-width: 0; display: flex; flex-direction: column;">
                    <div style="font-size:14px; font-weight:600; margin-bottom:6px; color:#222; display:flex; align-items:center; gap:6px;">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M9 11H15M9 15H15M9 7H15M5 3H19C20.1046 3 21 3.89543 21 5V19C21 20.1046 20.1046 21 19 21H5C3.89543 21 3 20.1046 3 19V5C3 3.89543 3.89543 3 5 3Z" stroke="#666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        Workflow Analysis
                    </div>
                    <div style="background:#fff; border-radius:6px; padding:12px; border:1px solid #e9ecef; box-shadow:0 1px 3px rgba(0,0,0,0.05); height: 70px; overflow-y: auto;">
                        <div style="margin-bottom:0px;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; color:#495057;">
                                <span style="font-weight:500; font-size:13px;">Top Stage(s)</span>
                                <span style="color:#1976d2; font-size:12px; font-weight:600;">${topStages && topStages.length > 0 ? topStages[0][1] : 0} counts</span>
                            </div>
                            <div style="display:flex; flex-wrap:wrap; gap:6px;">
                                ${topStages && topStages.length > 0 ? topStages.map(([stage, count]) => {
            const group = STAGE_GROUP_MAP[stage];
            let borderStyle = 'none';
            let borderWidth = '0px';
            let borderColor = 'transparent';

            if (group === 'Data-oriented') {
                borderStyle = 'solid';
                borderWidth = '1.5px';
                borderColor = '#666666';
            } else if (group === 'Model-oriented') {
                borderStyle = 'dashed';
                borderWidth = '1.5px';
                borderColor = '#666666';
            }

            return `
                                        <div style="display:inline-flex; align-items:center; margin-right:8px; margin-bottom:4px;">
                                            <div style="width:10px; height:12px; background-color:${this.colorScale(stage)}; border-radius:2px; margin-right:6px; flex-shrink:0; border:${borderWidth} ${borderStyle} ${borderColor}; align-self:center;"></div>
                                            <span style="color:#222; font-weight:600; font-size:13px; line-height:12px; display:flex; align-items:center;">${typeof LABEL_MAP !== 'undefined' ? (LABEL_MAP[stage] ?? stage) : stage}</span>
                                        </div>
                                    `;
        }).join('') : '<span style="color:#6c757d; font-size:13px; font-style:italic;">None</span>'}
                            </div>
                        </div>
                        <div style="flex: 1; display: none; flex-direction: column; justify-content: flex-end;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; color:#495057;">
                                <span style="font-weight:500; font-size:13px;">Top Transition(s)</span>
                                <span style="color:#1976d2; font-size:12px; font-weight:600;">${topTransitions && topTransitions.length > 0 ? topTransitions[0][1] : 0} counts</span>
                            </div>
                            <div style="display:flex; flex-direction:column; gap:3px;">
                                ${topTransitions && topTransitions.length > 0 ? topTransitions.map(([transition, count]) => {
            const [fromStage, toStage] = transition.split(' → ');

            // 获取from stage的border样式
            const fromGroup = STAGE_GROUP_MAP[fromStage];
            let fromBorderStyle = 'none';
            let fromBorderWidth = '0px';
            let fromBorderColor = 'transparent';

            if (fromGroup === 'Data-oriented') {
                fromBorderStyle = 'solid';
                fromBorderWidth = '1.5px';
                fromBorderColor = '#666666';
            } else if (fromGroup === 'Model-oriented') {
                fromBorderStyle = 'dashed';
                fromBorderWidth = '1.5px';
                fromBorderColor = '#666666';
            }

            // 获取to stage的border样式
            const toGroup = STAGE_GROUP_MAP[toStage];
            let toBorderStyle = 'none';
            let toBorderWidth = '0px';
            let toBorderColor = 'transparent';

            if (toGroup === 'Data-oriented') {
                toBorderStyle = 'solid';
                toBorderWidth = '1.5px';
                toBorderColor = '#666666';
            } else if (toGroup === 'Model-oriented') {
                toBorderStyle = 'dashed';
                toBorderWidth = '1.5px';
                toBorderColor = '#666666';
            }

            return `
                                        <div style="display:inline-flex; align-items:center; margin-right:8px; margin-bottom:4px;">
                                            <div style="width:10px; height:12px; background-color:${this.colorScale(fromStage)}; border-radius:2px; margin-right:6px; flex-shrink:0; border:${fromBorderWidth} ${fromBorderStyle} ${fromBorderColor}; align-self:center;"></div>
                                            <span style="color:#222; font-weight:600; font-size:13px; line-height:12px; display:flex; align-items:center;">${typeof LABEL_MAP !== 'undefined' ? (LABEL_MAP[fromStage] ?? fromStage) : fromStage}</span>
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin:0 4px;">
                                                <path d="M5 12H19M19 12L14 7M19 12L14 17" stroke="#666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                            </svg>
                                            <div style="width:10px; height:12px; background-color:${this.colorScale(toStage)}; border-radius:2px; margin-right:6px; flex-shrink:0; border:${toBorderWidth} ${toBorderStyle} ${toBorderColor}; align-self:center;"></div>
                                            <span style="color:#222; font-weight:600; font-size:13px; line-height:12px; display:flex; align-items:center;">${typeof LABEL_MAP !== 'undefined' ? (LABEL_MAP[toStage] ?? toStage) : toStage}</span>
                                        </div>
                                    `;
        }).join('') : '<span style="color:#6c757d; font-size:13px; font-style:italic;">None</span>'}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // 添加事件监听器到按钮
        setTimeout(() => {
            const clearBtn = this.clusterInfoContainer?.querySelector('#clear-cluster-selection-btn') as HTMLButtonElement;
            const titleBtn = this.clusterInfoContainer?.querySelector('#cluster-title-btn') as HTMLElement;

            if (clearBtn) {
                // 移除之前的事件监听器（如果有的话）
                clearBtn.removeEventListener('click', this.clearClusterSelection);
                // 添加新的事件监听器
                clearBtn.addEventListener('click', () => this.clearClusterSelection());
            }

            if (titleBtn) {
                // 添加cluster title的点击事件监听器
                titleBtn.addEventListener('click', () => this.scrollToCluster());
            }
        }, 0);
    }

    // 显示competition信息
    private showCompetitionInfo() {
        if (!this.clusterInfoContainer || !this.competitionInfo) return;

        const { description } = this.competitionInfo;

        if (!description) {
            this.clusterInfoContainer.style.display = 'none';
            return;
        }

        this.clusterInfoContainer.innerHTML = `
            <div style="font-size:16px; font-weight:700; margin-bottom:12px; line-height:1.3; padding-bottom:8px; border-bottom:1px solid #e9ecef;">
                <span style="color: #222;">Competition Description</span>
            </div>
            <div style="position: relative;">
                <div id="competition-description-content" style="background:#fff; border-radius:6px; padding:12px; border:1px solid #e9ecef; box-shadow:0 1px 3px rgba(0,0,0,0.05); height: 150px; overflow-y: auto; resize: vertical; min-height: 80px;">
                    <div style="font-size:13px; color:#222; line-height:1.5; font-weight:400;">
                        ${description}
                    </div>
                </div>
                <div id="competition-description-resizer" style="position: absolute; bottom: 0; left: 0; right: 0; height: 6px; cursor: ns-resize; background: transparent; border-radius: 0 0 6px 6px; z-index: 10;"></div>
            </div>
        `;

        // 添加拖拽调整高度的功能
        setTimeout(() => {
            const contentDiv = this.clusterInfoContainer?.querySelector('#competition-description-content') as HTMLElement;
            const resizer = this.clusterInfoContainer?.querySelector('#competition-description-resizer') as HTMLElement;

            if (contentDiv && resizer) {
                // 计算内容的完整高度
                const tempDiv = document.createElement('div');
                tempDiv.style.cssText = `
                    position: absolute;
                    visibility: hidden;
                    width: ${contentDiv.offsetWidth}px;
                    font-size: 13px;
                    line-height: 1.5;
                    padding: 12px;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                `;
                tempDiv.innerHTML = description;
                document.body.appendChild(tempDiv);

                const contentFullHeight = tempDiv.offsetHeight;
                document.body.removeChild(tempDiv);

                // 计算最大可用高度（视窗高度的80%）
                const maxAvailableHeight = Math.min(contentFullHeight, window.innerHeight * 0.8);

                // 设置最大高度
                contentDiv.style.maxHeight = maxAvailableHeight + 'px';

                let isResizing = false;
                let startY = 0;
                let startHeight = 0;

                resizer.addEventListener('mousedown', (e) => {
                    isResizing = true;
                    startY = e.clientY;
                    startHeight = parseInt(contentDiv.style.height) || contentDiv.offsetHeight;
                    document.body.style.cursor = 'ns-resize';
                    e.preventDefault();
                });

                document.addEventListener('mousemove', (e) => {
                    if (!isResizing) return;

                    const deltaY = e.clientY - startY;
                    const newHeight = Math.max(80, Math.min(maxAvailableHeight, startHeight + deltaY));
                    contentDiv.style.height = newHeight + 'px';
                });

                document.addEventListener('mouseup', () => {
                    if (isResizing) {
                        isResizing = false;
                        document.body.style.cursor = '';
                    }
                });
            }
        }, 0);
    }

    // 显示cluster概览信息
    private showClusterOverview() {
        if (!this.clusterInfoContainer) return;

        // 计算所有cluster的统计信息
        const clusterStats = new Map<string, { count: number; totalCells: number; totalVotes: number }>();

        this.data.forEach((nb, index) => {
            const kernelId = (nb as any).kernelVersionId?.toString();
            const simRow = kernelId ? this.similarityGroups.find((row: any) => row.kernelVersionId === kernelId) : null;
            if (simRow && simRow.cluster_id) {
                const clusterId = simRow.cluster_id;
                const current = clusterStats.get(clusterId) || { count: 0, totalCells: 0, totalVotes: 0 };
                current.count++;
                current.totalCells += nb.cells.length;

                // 添加投票信息
                if (this.voteData && this.voteData.length > 0) {
                    const voteRow = kernelId ? this.voteData.find((row: any) => row.kernelVersionId === kernelId) : null;
                    if (voteRow && voteRow.TotalVotes !== undefined) {
                        current.totalVotes += parseFloat(voteRow.TotalVotes) || 0;
                    }
                }

                clusterStats.set(clusterId, current);
            }
        });

        const totalClusters = clusterStats.size;
        const totalNotebooks = this.data.length;
        const avgNotebooksPerCluster = totalClusters > 0 ? Math.round(totalNotebooks / totalClusters) : 0;

        // 从summaryData中获取overall_summary
        let overallSummary = '';
        if (this.summaryData && this.summaryData.analysis_sections && this.summaryData.analysis_sections.overall_summary) {
            overallSummary = this.summaryData.analysis_sections.overall_summary;
        }

        this.clusterInfoContainer.innerHTML = `
            <div style="font-size:16px; font-weight:700; margin-bottom:12px; line-height:1.3; padding-bottom:8px; border-bottom:1px solid #e9ecef; display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <span style="color: #222;">Cluster Overview</span>
                    <div style="display:flex; align-items:center; gap:12px; font-size:13px; font-weight:400; color:#6c757d;">
                        <span>Total Clusters: <span style="color:#495057; font-weight:600;">${totalClusters}</span></span>
                        <span>Avg Cluster Size: <span style="color:#495057; font-weight:600;">${avgNotebooksPerCluster}</span></span>
                    </div>
                </div>
                <div style="font-size:12px; color:#4caf50; font-weight:500;">
                    💡 Click cluster labels to view details
                </div>
            </div>
            
            ${overallSummary ? `
                <div style="background:#fff; border-radius:6px; padding:12px; border:1px solid #e9ecef; box-shadow:0 1px 3px rgba(0,0,0,0.05); height: 150px; overflow-y: auto;">
                    <div style="font-size:13px; color:#222; line-height:1.5; font-weight:400;">${overallSummary}</div>
                </div>
            ` : ''}
        `;
    }

    // 清除cluster选择
    private clearClusterSelection() {
        const previousClusterId = this.selectedClusterId;
        this.selectedClusterId = null;

        // Track cluster clear action
        analytics.trackMatrixInteraction('icon_click', {
            iconType: 'clear_cluster',
            previousClusterId: previousClusterId,
            action: 'clear_selection',
            interaction_context: 'cluster_management'
        });

        // 保存当前的stage或transition选中状态

        // 优化：只更新cell的透明度，而不是重新绘制整个矩阵
        this.updateCellOpacityForClusterSelection();

        // 更新cluster信息显示
        this.updateClusterInfo();

        // 由于matrix不再跟随notebook detail tab的选择，这里不再恢复高亮状态

        // 派发cluster选择事件，通知LeftSidebar更新数据
        const clusterFilteredNotebooks = this.getClusterFilteredNotebooks();
        window.dispatchEvent(new CustomEvent('galaxy-cluster-selected', {
            detail: {
                clusterId: this.selectedClusterId,
                notebooks: clusterFilteredNotebooks
            }
        }));
    }

    // 优化：只更新cell的透明度和cluster标签样式，而不是重新绘制整个矩阵
    private updateCellOpacityForClusterSelection() {
        // 使用 D3 选择所有 matrix cells 并更新透明度
        d3.selectAll('.matrix-cell').each((d: any, i: number, nodes: any) => {
            const cell = d3.select(nodes[i]);
            const row = cell.attr('data-row');
            const nb = this.data[parseInt(row)];

            // 检查当前notebook是否属于选中的cluster
            let isInSelectedCluster = false;
            if (this.selectedClusterId && this.sortState === 3 && this.similarityGroups && this.similarityGroups.length > 0) {
                const kernelId = (nb as any)?.kernelVersionId?.toString();
                const simRow = kernelId ? this.similarityGroups.find((row: any) => row.kernelVersionId === kernelId) : null;
                isInSelectedCluster = simRow && simRow.cluster_id === this.selectedClusterId;
            }

            // 更新透明度 - 使用CSS类而不是直接设置opacity属性，避免与matrix-dim类冲突
            if (this.selectedClusterId && !isInSelectedCluster) {
                // 如果选中了cluster但当前notebook不属于该cluster，则灰掉
                cell.attr('opacity', 0.3).classed('cluster-dim', true).classed('matrix-dim', false);
            } else {
                // 否则恢复正常透明度，让CSS类控制透明度
                cell.attr('opacity', null).classed('cluster-dim', false);
            }
        });

        // 更新cluster标签的样式
        if (this.sortState === 3 && this.similarityGroups && this.similarityGroups.length > 0) {
            // 更新cluster标签的横线样式
            d3.selectAll('.cluster-labels line').each((d: any, i: number, nodes: any) => {
                const line = d3.select(nodes[i]);
                const clusterId = line.attr('data-cluster-id');
                const isSelected = this.selectedClusterId === clusterId;

                if (isSelected) {
                    line.attr('stroke', '#4caf50').attr('stroke-width', 3);
                } else {
                    line.attr('stroke', '#666').attr('stroke-width', 2);
                }
            });

            // 更新cluster标签文本样式
            d3.selectAll('.cluster-labels text').each((d: any, i: number, nodes: any) => {
                const text = d3.select(nodes[i]);
                const clusterId = text.attr('data-cluster-id');
                const textContent = text.text();
                const isSelected = this.selectedClusterId === clusterId;

                // 检查是否是cluster标题文本（包含"Cluster"字样）
                if (textContent && textContent.includes('Cluster')) {
                    if (isSelected) {
                        text.attr('fill', '#4caf50');
                    } else {
                        text.attr('fill', '#333');
                    }
                } else {
                    // 数量信息文本
                    if (isSelected) {
                        text.attr('fill', '#4caf50');
                    } else {
                        text.attr('fill', '#666');
                    }
                }
            });
        }
    }

    // 滚动到选中的cluster位置
    private scrollToCluster() {
        if (!this.selectedClusterId) return;

        // Track scroll to cluster action
        analytics.trackMatrixInteraction('icon_click', {
            iconType: 'scroll_to_cluster',
            clusterId: this.selectedClusterId,
            action: 'scroll_to_position',
            interaction_context: 'cluster_navigation'
        });

        const matrixContainer = this.node.querySelector('.matrix-container') as HTMLElement;
        if (!matrixContainer) return;

        // 获取当前排序后的notebook顺序
        const notebooks = this.data;
        const notebookOrder = this.notebookOrder.length ? this.notebookOrder : notebooks.map((_, i) => i);

        // 应用筛选
        const assignmentFilter = (this as any)._assignmentFilter || '';
        const studentFilter = (this as any)._studentFilter || '';
        const filteredNotebookOrder = notebookOrder.filter(idx => {
            const nb = notebooks[idx] as any;
            const matchAssignment = !assignmentFilter || nb.assignment === assignmentFilter;
            const matchStudent = !studentFilter || nb.student_id === studentFilter;
            return matchAssignment && matchStudent;
        });

        // 找到选中cluster的第一个notebook的位置
        let clusterStartIndex = -1;
        for (let i = 0; i < filteredNotebookOrder.length; i++) {
            const nb = notebooks[filteredNotebookOrder[i]] as any;
            const kernelId = nb && nb.kernelVersionId ? nb.kernelVersionId.toString() : null;
            const simRow = kernelId ? this.similarityGroups.find((row: any) => row.kernelVersionId === kernelId) : null;
            if (simRow && simRow.cluster_id === this.selectedClusterId) {
                clusterStartIndex = i;
                break;
            }
        }

        if (clusterStartIndex === -1) return;

        // 计算cluster的位置
        const cellWidth = 20;
        const rowPadding = 1;
        const notebookSpacing = 2;
        const groupGap = 20;

        // 计算到cluster开始位置的X坐标
        let targetX = 0;
        let currentGroupId: string | null = null;

        for (let i = 0; i < clusterStartIndex; i++) {
            const nb = notebooks[filteredNotebookOrder[i]] as any;

            // 检查是否需要添加组间距
            if (this.sortState === 3 && this.similarityGroups && this.similarityGroups.length > 0) {
                const kernelId = nb && nb.kernelVersionId ? nb.kernelVersionId.toString() : null;
                const simRow = kernelId ? this.similarityGroups.find((row: any) => row.kernelVersionId === kernelId) : null;
                const groupId = simRow ? simRow.cluster_id : null;

                // 如果这是新组，添加间距
                if (currentGroupId !== null && groupId !== currentGroupId) {
                    targetX += groupGap;
                }
                currentGroupId = groupId;
            }

            targetX += cellWidth + rowPadding + notebookSpacing;
        }

        // 添加一些偏移量，让cluster在视窗中居中显示
        const containerWidth = matrixContainer.clientWidth;
        const offsetX = Math.max(0, targetX - containerWidth / 2 + 100); // 100px的额外偏移

        // 平滑滚动到目标位置
        matrixContainer.scrollTo({
            left: offsetX,
            behavior: 'smooth'
        });

        // 保存滚动位置
        this.saveFilterState();
    }

    dispose(): void {
        // 清理定时器
        if (this.stageHoverTimeout) {
            clearTimeout(this.stageHoverTimeout);
        }
        if (this.transitionHoverTimeout) {
            clearTimeout(this.transitionHoverTimeout);
        }

        // 隐藏tooltip
        const tooltip = (window as any)._galaxyTooltip;
        if (tooltip) {
            tooltip.style.display = 'none';
            tooltip.style.opacity = '0';
        }

        // 移除事件监听器
        window.removeEventListener('galaxy-top-stats-updated', this._topStatsHandler);
        super.dispose();
    }
}