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
};


type StageDatum = {
    stage: string;
    count: number;
    norm_pos?: number;
    y?: number;
    size?: number;
};

export class LeftSidebar extends Widget {
    private data: Notebook[];
    private svg: d3.Selection<SVGSVGElement, unknown, null, undefined>;
    private stageData: StageDatum[] = [];
    private colorMap: Map<string, string>;
    private legendDiv: HTMLDivElement;
    private selection: any = null;
    private initialStageOrder: string[] = [];
    private overviewStageOrder: string[] = []; // 保存overview模式下的stage排序，用作cluster模式下相等位置的fallback
    private _resizeObserver: ResizeObserver | null = null;
    private hiddenStages: Set<string> = new Set(); // 隐藏的 stage
    private _renderTimeout: any = null; // 防抖定时器
    private _eventHandlers: { [key: string]: (e: any) => void } = {}; // 事件处理函数引用
  
    private isOverviewMode: boolean = true; // 标识是否为overview模式

    constructor(data: Notebook[], colorMap: Map<string, string>, isOverviewMode: boolean = true) {
        super();
        this.id = 'flow-chart-widget';
        this.title.label = 'Workflow';
        this.title.closable = true;
        this.addClass('flow-chart-widget');
        this.data = data;
        this.colorMap = colorMap;
        this.isOverviewMode = isOverviewMode;

        // 默认隐藏 Commented 和 Other
        this.hiddenStages = new Set(['10', '12']);

        // 初始化 stageData 顺序：基于在所有notebook中的平均相对位置
        const stageNotebookPositions = new Map<string, number[]>(); // stage -> array of average positions in each notebook
        
        this.data.forEach((nb) => {
            const codeCells = [...nb.cells]
                .sort((a, b) => a.cellId - b.cellId)
                .filter((d) => d.cellType === 'code');
            
            if (codeCells.length === 0) return;
            
            // 计算这个notebook中每个stage的平均相对位置
            const stagePositionsInThisNotebook = new Map<string, number[]>();
            codeCells.forEach((cell, index) => {
                const stage = String(cell["1st-level label"] ?? "None");
                if (stage === "None") return;
                
                // 计算这个cell在notebook中的相对位置
                const relativePos = codeCells.length > 1 ? index / (codeCells.length - 1) : 0.5;
                
                if (!stagePositionsInThisNotebook.has(stage)) {
                    stagePositionsInThisNotebook.set(stage, []);
                }
                stagePositionsInThisNotebook.get(stage)!.push(relativePos);
            });
            
            // 计算每个stage在这个notebook中的平均位置，并添加到全局记录中
            stagePositionsInThisNotebook.forEach((positions, stage) => {
                const avgPosInThisNotebook = positions.reduce((sum, pos) => sum + pos, 0) / positions.length;
                
                if (!stageNotebookPositions.has(stage)) {
                    stageNotebookPositions.set(stage, []);
                }
                stageNotebookPositions.get(stage)!.push(avgPosInThisNotebook);
            });
        });
        
        // 计算每个stage在所有包含它的notebook中的最终平均相对位置
        const stageAvgPositions = new Map<string, { avgPos: number, notebookCount: number }>();
        stageNotebookPositions.forEach((notebookPositions, stage) => {
            const avgPos = notebookPositions.reduce((sum, pos) => sum + pos, 0) / notebookPositions.length;
            stageAvgPositions.set(stage, { avgPos, notebookCount: notebookPositions.length });
        });
        
        // 按平均相对位置排序stages
        const sortedStages = Array.from(stageAvgPositions.entries())
            .sort((a, b) => a[1].avgPos - b[1].avgPos)
            .map(([stage, data]) => ({ stage: String(stage), count: 0 }));
        
        this.stageData = sortedStages;
        this.initialStageOrder = this.stageData.map(d => d.stage);
        // 保存overview模式下的stage排序作为fallback参考
        this.overviewStageOrder = [...this.initialStageOrder];

        this.render();

        // 清空 this.node
        this.node.innerHTML = '';
        this.node.style.display = 'flex';
        this.node.style.flexDirection = 'column';
        this.node.style.height = '100%';
        this.node.style.padding = '16px 16px 16px 16px'; // 恢复原来的底部内边距
        this.node.style.minWidth = '340px'; // 保证sidebar最小宽度不小于SVG

        // 右下角重置排序 icon
        const resetDiv = document.createElement('div');
        resetDiv.style.position = 'absolute';
        resetDiv.style.bottom = '8px'; // 与legend最后一行平齐
        resetDiv.style.right = '18px';
        resetDiv.style.zIndex = '10';
        resetDiv.style.cursor = 'pointer';
        resetDiv.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z" fill="currentColor"/></svg>`;
        resetDiv.onmouseenter = (e) => {
            resetDiv.style.background = '#f0f0f0';
            // 显示自定义tooltip
            const tooltip = document.getElementById('galaxy-tooltip');
            if (tooltip) {
                tooltip.innerHTML = 'Reset Order';
                tooltip.style.display = 'block';
                tooltip.style.left = e.clientX + 12 + 'px';
                tooltip.style.top = e.clientY + 12 + 'px';
            }
        };
        resetDiv.onmousemove = (e) => {
            // 更新tooltip位置
            const tooltip = document.getElementById('galaxy-tooltip');
            if (tooltip && tooltip.style.display === 'block') {
                tooltip.style.left = e.clientX + 12 + 'px';
                tooltip.style.top = e.clientY + 12 + 'px';
            }
        };
        resetDiv.onmouseleave = () => {
            resetDiv.style.background = 'none';
            // 隐藏tooltip
            const tooltip = document.getElementById('galaxy-tooltip');
            if (tooltip) {
                tooltip.style.display = 'none';
            }
        };
        resetDiv.onclick = () => {
            // 重置排序
            this.stageData = this.initialStageOrder.map(stage => {
                // 找到当前 stageData 对应的对象
                return this.stageData.find(d => d.stage === stage)!;
            });
            this.render();
        };
        // 容器需 position:relative
        this.node.style.position = 'relative';
        this.node.appendChild(resetDiv);

        // 中间 flowchart 区域
        const chartContainer = document.createElement('div');
        chartContainer.className = 'galaxy-flowchart-container';
        chartContainer.style.flex = '1 1 auto';
        chartContainer.style.overflow = 'hidden';  // 不滚动
        chartContainer.style.display = 'flex';
        chartContainer.style.flexDirection = 'column';
        this.node.appendChild(chartContainer);

        // 底部 legend
        this.legendDiv = document.createElement('div');
        this.legendDiv.className = 'galaxy-legend';
        this.legendDiv.style.display = 'block';
        this.legendDiv.style.overflow = 'visible';
        this.legendDiv.style.flex = 'none';
        this.legendDiv.style.maxHeight = 'none'; // 确保legend不会被截断
        this.legendDiv.style.margin = '0'; // 移除底部margin，让legend与refresh icon平齐
        this.legendDiv.style.padding = '0';
        this.legendDiv.style.height = 'auto'; // 根据内容自适应高度
        this.legendDiv.style.minHeight = '0'; // 允许收缩
        this.node.appendChild(this.legendDiv);

        // SVG 渲染到中间
        const svgElement = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svgElement.setAttribute('viewBox', '0 0 400 600');
        svgElement.setAttribute('preserveAspectRatio', 'xMidYMin meet');
        svgElement.style.width = '100%';
        svgElement.style.overflow = 'visible';
        svgElement.style.flex = '1 1 auto';
        svgElement.style.height = '100%';  // 关键：撑满 chartContainer
        svgElement.style.marginBottom = '0';  // 去掉底部冗余间距
        chartContainer.appendChild(svgElement);
        this.svg = d3.select(svgElement);

        // 全局 tooltip div
        if (!document.getElementById('galaxy-tooltip')) {
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
        }

        this._eventHandlers['galaxy-selection-cleared'] = (e: any) => {
            const { tabId } = e.detail || {};
            // 如果是 overview 模式，处理所有 notebook detail 的清除事件
            // 如果是 notebook detail 模式，只处理当前 tab 的事件
            const currentTabId = this.getTabId();

            // 如果事件来自 notebook detail widget，总是处理（因为 overview 需要响应所有 notebook 的清除）
            if (tabId && tabId.startsWith('notebook-detail-widget-')) {
                this.selection = null;
                // 清除全局筛选状态变量
                const flowSelectionKey = `_galaxyFlowSelection_${tabId}`;
                const stageSelectionKey = `_galaxyStageSelection_${tabId}`;
                (window as any)[stageSelectionKey] = null;
                (window as any)[flowSelectionKey] = null;
                // 清除hover状态
                (window as any)._galaxyFlowHoverStage = null;
                (window as any)._galaxyFlowHoverInfo = null;
                this.saveFilterState();
                this.render();
            } else if (currentTabId === 'overview' || tabId === currentTabId) {

                this.selection = null;
                // 清除全局筛选状态变量
                const flowSelectionKey = `_galaxyFlowSelection_${tabId}`;
                const stageSelectionKey = `_galaxyStageSelection_${tabId}`;
                (window as any)[stageSelectionKey] = null;
                (window as any)[flowSelectionKey] = null;
                // 清除hover状态
                (window as any)._galaxyFlowHoverStage = null;
                (window as any)._galaxyFlowHoverInfo = null;
                this.saveFilterState();
                this.render();
            }
        };
        window.addEventListener('galaxy-selection-cleared', this._eventHandlers['galaxy-selection-cleared']);

        // 监听 stage 选中事件（按tab隔离）
        this._eventHandlers['galaxy-stage-selected'] = (e: any) => {
            const { stage, tabId } = e.detail;
            const currentTabId = this.getTabId();
            // 只处理当前tab的事件
            if (tabId === currentTabId) {
                this.selection = { type: 'stage', stage };
                this.saveFilterState();
                this.render();
            }
        };
        window.addEventListener('galaxy-stage-selected', this._eventHandlers['galaxy-stage-selected']);

        // 监听 flow 选中事件（按tab隔离）
        this._eventHandlers['galaxy-flow-selected'] = (e: any) => {
            const { from, to, tabId } = e.detail;
            const currentTabId = this.getTabId();
            // 只处理当前tab的事件
            if (tabId === currentTabId) {
                this.selection = { type: 'flow', from, to };
                this.saveFilterState();
                this.render();
            }
        };
        window.addEventListener('galaxy-flow-selected', this._eventHandlers['galaxy-flow-selected']);
        // 监听 matrix 筛选事件，flow chart 跟随筛选
        this._eventHandlers['galaxy-matrix-filtered'] = (e: any) => {
            const filteredData = e.detail?.notebooks ?? [];
            this.setData(filteredData, this.colorMap);
        };
        window.addEventListener('galaxy-matrix-filtered', this._eventHandlers['galaxy-matrix-filtered']);

        // 监听 cluster 选择事件，flow chart 跟随cluster筛选
        this._eventHandlers['galaxy-cluster-selected'] = (e: any) => {
            const clusterData = e.detail?.notebooks ?? [];
            this.setData(clusterData, this.colorMap);

            // 清除stage和flow选中状态
            this.selection = null;
            const tabId = this.getTabId();
            const stageSelectionKey = `_galaxyStageSelection_${tabId}`;
            const flowSelectionKey = `_galaxyFlowSelection_${tabId}`;
            (window as any)[stageSelectionKey] = null;
            (window as any)[flowSelectionKey] = null;
            // 清除hover状态
            (window as any)._galaxyFlowHoverStage = null;
            (window as any)._galaxyFlowHoverInfo = null;
            this.saveFilterState();
        };
        window.addEventListener('galaxy-cluster-selected', this._eventHandlers['galaxy-cluster-selected']);

        this.render();
    }

    private render(): void {
        // 防抖处理，避免频繁渲染
        if (this._renderTimeout) {
            clearTimeout(this._renderTimeout);
        }

        this._renderTimeout = setTimeout(() => {
            this._renderInternal();
        }, 16); // 约60fps的刷新率
    }

    // 立即渲染，不经过防抖（用于拖拽等需要即时反馈的场景）
    private renderImmediate(): void {
        if (this._renderTimeout) {
            clearTimeout(this._renderTimeout);
            this._renderTimeout = null;
        }
        this._renderInternal();
    }

    private _renderInternal(): void {
        // 添加距离比例箭头
        const addDistanceBasedArrow = (path: d3.Selection<SVGPathElement, unknown, null, undefined>, arrowSize = 6) => {
            const pathNode = path.node();
            if (!pathNode) return;

            const totalLength = pathNode.getTotalLength();
            if (totalLength === 0) return;

            // 起点终点
            const start = pathNode.getPointAtLength(0);
            const end = pathNode.getPointAtLength(totalLength);

            // 计算距离
            const dx = end.x - start.x;
            const dy = end.y - start.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            // 根据距离决定箭头位置比例 - 都靠近终点
            let arrowPosition = 0.7; // 默认靠近终点
            if (distance > 300) {
                arrowPosition = 0.6; // 长距离，稍微远离终点
            } else if (distance > 150) {
                arrowPosition = 0.65; // 中等距离
            } else {
                arrowPosition = 0.75; // 短距离，更靠近终点
            }

            // 获取flow源头的颜色
            const fromStage = pathNode.getAttribute("data-from-stage");
            const sourceColor = fromStage
                ? this.colorMap.get(fromStage) || "#2c3e50"
                : "#2c3e50";

            // 智能调整箭头大小
            const flowStrokeWidth = parseFloat(
                pathNode.getAttribute("stroke-width") || "1",
            );
            let finalArrowSize;
            if (flowStrokeWidth > 8) {
                finalArrowSize = flowStrokeWidth * 0.8;
            } else {
                const adjustedArrowSize = Math.min(arrowSize, totalLength * 0.15);
                finalArrowSize = Math.max(adjustedArrowSize, 4);
            }

            const parentNode = pathNode.parentNode as Element;
            if (!parentNode) return;

            // 检查是否已经存在箭头，避免重复添加
            const existingArrow = d3.select(parentNode).select(`.distance-arrow[data-path-id="${pathNode.getAttribute('data-path-id')}"]`);
            if (!existingArrow.empty()) return;

            // 在指定位置添加单个箭头
            const length = totalLength * arrowPosition;
            const pt = pathNode.getPointAtLength(length);

            // 计算箭头角度
            const before = pathNode.getPointAtLength(Math.max(0, length - 2));
            const after = pathNode.getPointAtLength(Math.min(totalLength, length + 2));
            const angleRad = Math.atan2(after.y - before.y, after.x - before.x);
            let bestAngle = (angleRad * 180) / Math.PI + 180; // 旋转180度修正方向

            // 添加箭头
            d3.select(parentNode)
                .append("g")
                .attr("class", "distance-arrow")
                .attr("data-path-id", pathNode.getAttribute('data-path-id'))
                .attr(
                    "transform",
                    `translate(${pt.x}, ${pt.y}) rotate(${bestAngle})`,
                )
                .append("path")
                .attr(
                    "d",
                    `M ${-finalArrowSize / 2} 0 L ${finalArrowSize / 2} ${-finalArrowSize / 2} L ${finalArrowSize / 2} ${finalArrowSize / 2} Z`,
                )
                .attr("fill", sourceColor)
                .attr("stroke", sourceColor)
                .attr("stroke-width", 1.2)
                .attr("stroke-linejoin", "round")
                .attr("opacity", 1);
        };

        // --- 更新顶部标题和返回按钮 ---
        let header = this.node.querySelector('.galaxy-header') as HTMLDivElement;
        if (!header) {
            header = document.createElement('div');
            header.className = 'galaxy-header';
            header.style.position = 'absolute';
            header.style.top = '12px';
            header.style.left = '18px';
            header.style.zIndex = '10';
            header.style.display = 'flex';
            header.style.alignItems = 'center';
            header.style.gap = '8px';
            this.node.appendChild(header);
        }

        // 根据 selection 类型渲染标题和返回按钮
        if (this.selection?.type === 'stage') {
            header.innerHTML = `
                <div style="cursor: pointer; display: flex; align-items: center; gap: 4px;" onclick="this.clearSelection()">
                    <svg width="16" height="16" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M15 10H5M5 10L10 15M5 10L10 5" stroke="#888" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <span style="font-weight: 600; color: #333;">${LABEL_MAP[this.selection.stage] ?? this.selection.stage}</span>
            `;
        } else if (this.selection?.type === 'flow') {
            header.innerHTML = `
                <div style="cursor: pointer; display: flex; align-items: center; gap: 4px;" onclick="this.clearSelection()">
                    <svg width="16" height="16" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M15 10H5M5 10L10 15M5 10L10 5" stroke="#888" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <span style="font-weight: 600; color: #333;">${LABEL_MAP[this.selection.from] ?? this.selection.from} → ${LABEL_MAP[this.selection.to] ?? this.selection.to}</span>
            `;
        } else {
            header.innerHTML = '';
        }

        // 绑定返回按钮的点击事件
        const backButton = header.querySelector('div');
        if (backButton) {
            backButton.onclick = () => {
                this.selection = null;
                // 清除全局选中状态（按tab隔离）
                const tabId = this.getTabId();
                const flowSelectionKey = `_galaxyFlowSelection_${tabId}`;
                const stageSelectionKey = `_galaxyStageSelection_${tabId}`;
                (window as any)[stageSelectionKey] = null;
                (window as any)[flowSelectionKey] = null;
                // 清除hover状态
                (window as any)._galaxyFlowHoverStage = null;
                (window as any)._galaxyFlowHoverInfo = null;
                window.dispatchEvent(new CustomEvent('galaxy-selection-cleared', { detail: { tabId: this.getTabId() } }));
                this.render();
            };
        }

        this.svg.selectAll('*').remove();
        // 由于SVG legend被注释掉了，不再需要预留legend区域高度
        const chartPadding = 30;  // 减少底部padding
        // 计算SVG高度，基于yScale的范围
        const virtualHeight = 1000; // 使用固定的逻辑高度
        // SVG总高度 = flowchart高度 + padding（不再预留legend区域）
        const svgHeight = virtualHeight + chartPadding;
        // 设置 viewBox
        this.svg.attr("viewBox", `0 0 400 ${svgHeight}`);



        // 保证 stageData 里的 stage 都是 string
        this.stageData.forEach(d => {
            d.stage = String(d.stage);
        });
        this.stageData.forEach(d => {
            if (!this.colorMap.has(d.stage)) {
                console.warn('colorMap 缺少 stage:', d.stage);
            }
        });
        const stageStats = new Map<string, { count: number }>();
        const transitions: Map<string, number> = new Map();

        this.data.forEach((nb) => {
            // 只保留 code cell
            const codeCells = [...nb.cells]
                .sort((a, b) => a.cellId - b.cellId)
                .filter((d) => d.cellType === 'code');
            const stageSeq: string[] = [];
            codeCells.forEach((cell) => {
                const stage = String(cell["1st-level label"] ?? "None");
                if (!stageStats.has(stage)) {
                    stageStats.set(stage, {
                        count: 0
                    });
                }
                stageStats.get(stage)!.count++;
                if (stageSeq.length === 0 || stageSeq[stageSeq.length - 1] !== stage) {
                    stageSeq.push(stage);
                }
            });

            // flow 统计：使用已经构建好的stageSeq计算transitions
            for (let i = 0; i < stageSeq.length - 1; i++) {
                const from = stageSeq[i];
                const to = stageSeq[i + 1];
                if (from !== "None" && to !== "None") {
                    const key = `${from}->${to}`;
                    transitions.set(key, (transitions.get(key) || 0) + 1);
                }
            }
        });

        // 只更新统计信息，不重排顺序
        this.stageData.forEach((d) => {
            const info = stageStats.get(d.stage) || { count: 0 };
            d.count = info.count;
        });

        // 只对未隐藏且 count>0 的 stage 重新分布 norm_pos
        const normVisibleStages = this.stageData.filter(d => !this.hiddenStages.has(d.stage) && d.count > 0);
        normVisibleStages.forEach((d, i) => {
            d.norm_pos = normVisibleStages.length > 1 ? i / (normVisibleStages.length - 1) : 0.5;
        });

        // 使用yScale来分布block的位置
        const yScale = d3.scaleLinear().domain([0, 1]).range([10, virtualHeight - 50]);
        const renderMaxCount = d3.max(this.stageData, (d) => d.count) || 1;
        const sizeScale = d3.scaleLinear().domain([0, renderMaxCount]).range([20, 80]);

        const countValues = Array.from(transitions.values());
        const maxFlowCount = d3.max(countValues) || 1;
        const minFlowCount = d3.min(countValues) || 0;
        const minWidth = 2;
        const maxWidth = 26;

        const strokeScale = (count: number) => {
            if (count <= 0) return 0;
            if (maxFlowCount <= 5) {
                // 离散情况直接写死
                return [0, 2, 4][count] || 5;
            }
            const t = (count - minFlowCount) / (maxFlowCount - minFlowCount);
            return minWidth + Math.pow(t, 0.4) * (maxWidth - minWidth);
        };

        const svg = this.svg;
        const defs = svg.append("defs");
        const g = svg.append("g").attr("transform", "translate(200, 0)");

        // 添加SVG背景点击事件，用于清除selection
        svg.on("click", (event) => {
            // 如果点击的是SVG背景（不是具体的元素），则清除selection
            if (event.target === svg.node()) {
                this.selection = null;
                // 清除全局选中状态（按tab隔离）
                const tabId = this.getTabId();
                const flowSelectionKey = `_galaxyFlowSelection_${tabId}`;
                const stageSelectionKey = `_galaxyStageSelection_${tabId}`;
                (window as any)[stageSelectionKey] = null;
                (window as any)[flowSelectionKey] = null;
                this.render();
                window.dispatchEvent(new CustomEvent('galaxy-selection-cleared', { detail: { tabId: this.getTabId() } }));
            }
        });


        // 过滤掉隐藏的 stage 和 count=0 的 stage
        const visibleStages = this.stageData.filter(d => !this.hiddenStages.has(d.stage) && d.count > 0);
        // 重新构建 stageMap 只包含可见且 count>0 的 stage
        const stageMap = new Map<string, { x: number; y: number; width: number; height: number; centerX: number; centerY: number }>();

        visibleStages.forEach((d) => {
            const width = 60; // 固定宽度
            const height = sizeScale(d.count); // 高度根据count变化
            const x = -width / 2; // 居中
            const y = yScale(d.norm_pos!); // 使用yScale分布位置

            d.y = y;
            d.size = height;
            stageMap.set(d.stage, {
                x,
                y,
                width,
                height,
                centerX: x + width / 2,
                centerY: y + height / 2
            });
        });

        // 拖拽行为
        let isDragging = false;
        let dragStartY = 0;
        let draggedElement: d3.Selection<SVGRectElement, StageDatum, any, any> | null = null;
        let animationFrameId: number | null = null;
        let dragStartTime = 0;
        let dragStartPosition: { x: number; y: number } | null = null;

        const drag = d3.drag<SVGRectElement, StageDatum>()
            .on('start', function (event, d) {
                dragStartY = event.y;
                isDragging = false;
                draggedElement = d3.select(this);
                draggedElement.raise();

                // 记录drag开始信息
                dragStartTime = Date.now();
                dragStartPosition = { x: event.x, y: event.y };

                // 添加拖拽时的视觉反馈 - 使用CSS类而不是内联样式
                draggedElement.classed('dragging', true);
            })
            .on('drag', (event, d) => {
                // 降低拖拽阈值，提高响应性
                if (Math.abs(event.y - dragStartY) > 2) {
                    isDragging = true;
                }

                if (isDragging && draggedElement) {
                    // 使用requestAnimationFrame优化拖拽性能
                    if (animationFrameId) {
                        cancelAnimationFrame(animationFrameId);
                    }

                    animationFrameId = requestAnimationFrame(() => {
                        const stageInfo = stageMap.get(d.stage);
                        if (stageInfo && draggedElement) {
                            const newY = event.y - stageInfo.height / 2;
                            const originalY = stageInfo.y;
                            const deltaY = newY - originalY;
                            // 使用transform而不是改变y属性，提高性能
                            draggedElement.style('transform', `translateY(${deltaY}px)`);
                        }
                    });
                }
            })
            .on('end', (event, d) => {
                // 清理动画帧
                if (animationFrameId) {
                    cancelAnimationFrame(animationFrameId);
                    animationFrameId = null;
                }

                if (draggedElement) {
                    // 恢复视觉样式
                    draggedElement.classed('dragging', false);
                    // 添加恢复动画类
                    draggedElement.classed('dragging-end', true);
                    // 清除transform
                    draggedElement.style('transform', '');
                    // 移除恢复动画类
                    setTimeout(() => {
                        if (draggedElement) {
                            draggedElement.classed('dragging-end', false);
                        }
                    }, 150);
                }

                if (isDragging) {
                    // 追踪stage move事件
                    if (dragStartPosition && dragStartTime) {
                        const moveDistance = Math.sqrt(
                            Math.pow(event.x - dragStartPosition.x, 2) + 
                            Math.pow(event.y - dragStartPosition.y, 2)
                        );
                        const moveDuration = Date.now() - dragStartTime;

                        analytics.trackStageMove({
                            stage: d.stage,
                            stageLabel: LABEL_MAP[d.stage] || d.stage,
                            oldPosition: dragStartPosition,
                            newPosition: { x: event.x, y: event.y },
                            moveDistance: moveDistance,
                            moveDuration: moveDuration,
                            stageId: `stage-${d.stage}`,
                            flowchartContext: this.isOverviewMode ? 'overview' : 'notebook_detail'
                        });
                    }

                    // 拖动才重排
                    let closest = this.stageData[0];
                    let minDist = Math.abs(event.y - (closest.y ?? 0));
                    for (const s of this.stageData) {
                        const dist = Math.abs(event.y - (s.y ?? 0));
                        if (dist < minDist) {
                            minDist = dist;
                            closest = s;
                        }
                    }
                    const oldIdx = this.stageData.findIndex(s => s.stage === d.stage);
                    const newIdx = this.stageData.findIndex(s => s.stage === closest.stage);
                    if (oldIdx !== newIdx) {
                        const arr = [...this.stageData];
                        arr.splice(oldIdx, 1);
                        arr.splice(newIdx, 0, d);
                        this.stageData = arr;
                        // 使用立即渲染来确保拖拽结束后的即时反馈
                        this.renderImmediate();
                    } else {
                        // 如果没有位置变化，清除transform即可
                        if (draggedElement) {
                            draggedElement.style('transform', '');
                        }
                    }
                }

                draggedElement = null;
                // 关键：短暂延迟后重置 isDragging，保证 pointerup 能正确识别
                setTimeout(() => { isDragging = false; }, 0);
            });

        // === 渲染 transition（flow-link） ===
        transitions.forEach((count, key) => {
            const [from, to] = key.split("->");
            const fromPos = stageMap.get(from);
            const toPos = stageMap.get(to);
            if (!fromPos || !toPos) return; // 只渲染可见的

            const x1 = fromPos.centerX;
            const y1 = fromPos.centerY;
            const x2 = toPos.centerX;
            const y2 = toPos.centerY;
            const side = y2 > y1 ? 1 : -1;

            const dy = Math.abs(y2 - y1);
            const offset = Math.min(dy * 0.5, 300);
            const ctrlX1 = x1 + side * offset;
            const ctrlX2 = x2 + side * offset;

            const gradientId = `grad-${from}-${to}`;
            const grad = defs.append("linearGradient")
                .attr("id", gradientId)
                .attr("gradientUnits", "userSpaceOnUse")
                .attr("x1", x1)
                .attr("y1", y1)
                .attr("x2", x2)
                .attr("y2", y2);

            grad.append("stop").attr("offset", "0%").attr("stop-color", this.colorMap.get(from) || '#ccc').attr("stop-opacity", 1);
            grad.append("stop").attr("offset", "100%").attr("stop-color", this.colorMap.get(to) || '#ccc').attr("stop-opacity", 0.2);

            g.append("path")
                .attr("d", `M${x1},${y1} C${ctrlX1},${y1} ${ctrlX2},${y2} ${x2},${y2}`)
                .attr("stroke", `url(#${gradientId})`)
                .attr("stroke-width", strokeScale(count))
                .attr("data-original-stroke-width", strokeScale(count))
                .attr("data-from-stage", from)
                .attr("data-path-id", `flow-${from}-${to}`)
                .attr("fill", "none")
                .attr("opacity", 0.7)
                .attr("class", (d) => `flow-link link-from-${from} link-to-${to}`)
                .on("mouseover", (event, d) => {
                    // 在拖拽过程中忽略hover效果
                    if (isDragging) return;

                    // 只有在没有选中状态时才应用hover效果
                    if (!this.selection) {
                        d3.selectAll(".flow-link").attr("opacity", 0.05);
                        const highlightedLinks = d3.selectAll(`.link-from-${from}.link-to-${to}`).attr("opacity", 1);

                        // 添加箭头
                        highlightedLinks.each(function () {
                            const linkElement = d3.select(this);
                            const strokeWidth = parseFloat(linkElement.attr("data-original-stroke-width") || "1");
                            const arrowSize = Math.max(8, strokeWidth * 1.5);
                            addDistanceBasedArrow(linkElement as any, arrowSize);
                        });

                        // 联动高亮 matrix pattern
                        if (this.isOverviewMode) window.dispatchEvent(new CustomEvent('galaxy-transition-hover', { detail: { from, to, tabId: this.getTabId() } }));
                    }
                    // tooltip
                    const tooltip = document.getElementById('galaxy-tooltip');
                    tooltip!.innerHTML = `<strong>${LABEL_MAP[from] ?? from} → ${LABEL_MAP[to] ?? to}</strong><br>Count: ${count}`;
                    tooltip!.style.display = 'block';
                })
                .on("mousemove", (event) => {
                    // 在拖拽过程中忽略tooltip移动
                    if (isDragging) return;

                    const tooltip = document.getElementById('galaxy-tooltip');
                    tooltip!.style.left = event.clientX + 12 + 'px';
                    tooltip!.style.top = event.clientY + 12 + 'px';
                })
                .on("mouseout", (event) => {
                    // 只有在没有选中状态时才恢复默认样式
                    if (!this.selection) {
                        d3.selectAll(".flow-link").attr("opacity", 0.7);
                        // 清除动态创建的箭头
                        d3.selectAll(".distance-arrow").remove();
                        // hover离开时恢复默认的border样式
                        d3.selectAll(`.stage-rect`).each((d, i, nodes) => {
                            const rect = d3.select(nodes[i]);
                            const stage = rect.datum() as StageDatum;
                            const group = STAGE_GROUP_MAP[stage.stage];
                            if (group === 'Data-oriented' || group === 'Model-oriented') {
                                rect.attr("stroke", "#666666").attr("stroke-width", 5).attr("stroke-dasharray", group === 'Model-oriented' ? "8" : "none");
                            } else {
                                rect.attr("stroke", "none").attr("stroke-width", 0);
                            }
                        });
                        // 取消联动高亮
                        if (this.isOverviewMode) window.dispatchEvent(new CustomEvent('galaxy-transition-hover', { detail: { from: null, to: null, tabId: this.getTabId() } }));
                    } else {
                        // 如果有选中状态，直接应用选中效果
                        if (this.selection.type === 'flow') {
                            d3.selectAll(".flow-link").attr("opacity", 0.05);
                            const highlightedLinks = d3.selectAll(`.link-from-${this.selection.from}.link-to-${this.selection.to}`).attr("opacity", 1);
                            // 为选中的flow添加箭头
                            highlightedLinks.each(function () {
                                const linkElement = d3.select(this);
                                const strokeWidth = parseFloat(linkElement.attr("data-original-stroke-width") || "1");
                                const arrowSize = Math.max(8, strokeWidth * 1.5);
                                addDistanceBasedArrow(linkElement as any, arrowSize);
                            });
                            // 选中状态下保持原有样式，只有原本有边框的才保持边框
                            d3.selectAll(`.stage-${this.selection.from}, .stage-${this.selection.to}`).each((d, i, nodes) => {
                                const rect = d3.select(nodes[i]);
                                const stage = rect.datum() as StageDatum;
                                const group = STAGE_GROUP_MAP[stage.stage];
                                if (group === 'Data-oriented' || group === 'Model-oriented') {
                                    rect.attr("stroke", "#666666").attr("stroke-width", 5).attr("stroke-dasharray", group === 'Model-oriented' ? "8" : "none");
                                } else {
                                    rect.attr("stroke", "none").attr("stroke-width", 0);
                                }
                            });
                        } else if (this.selection.type === 'stage') {
                            d3.selectAll(".flow-link").attr("opacity", 0.05);
                            const highlightedLinks = d3.selectAll(`.link-from-${this.selection.stage}, .link-to-${this.selection.stage}`).attr("opacity", 0.9);
                            // 为选中的stage相关的flow添加箭头
                            highlightedLinks.each(function () {
                                const linkElement = d3.select(this);
                                const strokeWidth = parseFloat(linkElement.attr("data-original-stroke-width") || "1");
                                const arrowSize = Math.max(8, strokeWidth * 1.5);
                                addDistanceBasedArrow(linkElement as any, arrowSize);
                            });
                            // 选中状态下保持原有样式，只有原本有边框的才保持边框
                            d3.selectAll(`.stage-${this.selection.stage}`).each((d, i, nodes) => {
                                const rect = d3.select(nodes[i]);
                                const stage = rect.datum() as StageDatum;
                                const group = STAGE_GROUP_MAP[stage.stage];
                                if (group === 'Data-oriented' || group === 'Model-oriented') {
                                    rect.attr("stroke", "#666666").attr("stroke-width", 5).attr("stroke-dasharray", group === 'Model-oriented' ? "8" : "none");
                                } else {
                                    rect.attr("stroke", "none").attr("stroke-width", 0);
                                }
                            });
                        }
                    }
                    // tooltip
                    const tooltip = document.getElementById('galaxy-tooltip');
                    tooltip!.style.display = 'none';
                })
                .on("click", (event) => {
                    // 如果当前已经选中了这个flow，则取消选中
                    if (this.selection && this.selection.type === 'flow' && this.selection.from === from && this.selection.to === to) {
                        this.selection = null;
                        // 清除全局选中状态（按tab隔离）
                        const tabId = this.getTabId();
                        const flowSelectionKey = `_galaxyFlowSelection_${tabId}`;
                        const stageSelectionKey = `_galaxyStageSelection_${tabId}`;
                        (window as any)[flowSelectionKey] = null;
                        (window as any)[stageSelectionKey] = null;
                        this.saveFilterState();
                        this.render();
                        window.dispatchEvent(new CustomEvent('galaxy-selection-cleared', { detail: { tabId: this.getTabId() } }));
                    } else {
                        // 选中新的flow
                        this.selection = { type: 'flow', from, to };
                        // 设置全局选中状态（按tab隔离）
                        const tabId = this.getTabId();
                        const flowSelectionKey = `_galaxyFlowSelection_${tabId}`;
                        const stageSelectionKey = `_galaxyStageSelection_${tabId}`;
                        (window as any)[flowSelectionKey] = { from, to };
                        (window as any)[stageSelectionKey] = null;
                        this.render();
                        window.dispatchEvent(new CustomEvent('galaxy-flow-selected', { detail: { from, to, tabId: this.getTabId() } }));
                    }
                });
        });
        // === END transition ===

        // === 渲染 block rect（无透明度） ===
        g.selectAll('stage-rect')
            .data(visibleStages)
            .enter()
            .append('rect')
            .attr('x', (d) => stageMap.get(d.stage)!.x)
            .attr('y', (d) => stageMap.get(d.stage)!.y)
            .attr('width', (d) => stageMap.get(d.stage)!.width)
            .attr('height', (d) => stageMap.get(d.stage)!.height)
            .attr('rx', 6) // 添加圆角
            .attr('ry', 6) // 添加圆角
            .attr('fill', (d) => this.colorMap.get(d.stage) || '#ccc')
            .attr('class', (d) => `stage-rect stage-${d.stage}`)
            .attr('stroke', (d) => {
                const group = STAGE_GROUP_MAP[d.stage];
                if (group === 'Data-oriented' || group === 'Model-oriented') {
                    return '#666666'; // 统一使用灰色
                }
                return 'none'; // 其他类别无border
            })
            .attr('stroke-width', (d) => {
                const group = STAGE_GROUP_MAP[d.stage];
                if (group === 'Data-oriented' || group === 'Model-oriented') {
                    return 5; // 更粗的边框
                }
                return 0;
            })
            .attr('stroke-dasharray', (d) => {
                const group = STAGE_GROUP_MAP[d.stage];
                if (group === 'Model-oriented') {
                    return '8'; // 虚线样式
                }
                return 'none'; // 实线样式
            })
            .on("mouseover", (event, d) => {
                const stage = d.stage;
                // 在拖拽过程中忽略hover效果
                if (isDragging) return;

                // 只有在没有选中状态时才应用hover效果
                if (!this.selection) {
                    d3.selectAll(".flow-link").attr("opacity", 0.05);
                    const highlightedLinks = d3.selectAll(`.link-from-${stage}, .link-to-${stage}`).attr("opacity", 0.9);

                    // 添加箭头
                    highlightedLinks.each(function () {
                        const linkElement = d3.select(this);
                        const strokeWidth = parseFloat(linkElement.attr("data-original-stroke-width") || "1");
                        const arrowSize = Math.max(8, strokeWidth * 1.5);
                        addDistanceBasedArrow(linkElement as any, arrowSize);
                    });

                    // 联动高亮
                    if (this.isOverviewMode) window.dispatchEvent(new CustomEvent('galaxy-stage-hover', { detail: { stage, tabId: this.getTabId() } }));
                } else {
                    // 如果有选中状态，不触发hover事件，避免minimap高亮
                }
                // tooltip
                const tooltip = document.getElementById('galaxy-tooltip');
                const group = STAGE_GROUP_MAP[stage];
                // 只有 Data-oriented 和 Model-oriented 需要标注
                const groupLabel = (group === 'Data-oriented' || group === 'Model-oriented') ? `${group}<br>` : '';
                tooltip!.innerHTML = `<strong>${LABEL_MAP[stage] ?? stage}</strong><br>${groupLabel}Count: ${d.count}`;
                tooltip!.style.display = 'block';
            })
            .on("mousemove", (event) => {
                // 在拖拽过程中忽略tooltip移动
                if (isDragging) return;

                const tooltip = document.getElementById('galaxy-tooltip');
                tooltip!.style.left = event.clientX + 12 + 'px';
                tooltip!.style.top = event.clientY + 12 + 'px';
            })
            .on("mouseout", (event, d) => {
                // const stage = d.stage;
                
                // 只有在没有选中状态时才恢复默认样式
                if (!this.selection) {
                    d3.selectAll(".flow-link").attr("opacity", 0.7);
                    // 清除动态创建的箭头
                    d3.selectAll(".distance-arrow").remove();
                    // hover离开时恢复默认的border样式
                    d3.selectAll(`.stage-rect`).each((d, i, nodes) => {
                        const rect = d3.select(nodes[i]);
                        const stage = rect.datum() as StageDatum;
                        const group = STAGE_GROUP_MAP[stage.stage];
                        if (group === 'Data-oriented' || group === 'Model-oriented') {
                            rect.attr("stroke", "#666666").attr("stroke-width", 5).attr("stroke-dasharray", group === 'Model-oriented' ? "8" : "none");
                        } else {
                            rect.attr("stroke", "none").attr("stroke-width", 0);
                        }
                    });
                    // 联动高亮取消
                    if (this.isOverviewMode) window.dispatchEvent(new CustomEvent('galaxy-stage-hover', { detail: { stage: null, tabId: this.getTabId() } }));
                } else {
                    // 如果有选中状态，直接应用选中效果
                    if (this.selection.type === 'flow') {
                        d3.selectAll(".flow-link").attr("opacity", 0.05);
                        const highlightedLinks = d3.selectAll(`.link-from-${this.selection.from}.link-to-${this.selection.to}`).attr("opacity", 1);
                        // 为选中的flow添加箭头
                        highlightedLinks.each(function () {
                            const linkElement = d3.select(this);
                            const strokeWidth = parseFloat(linkElement.attr("data-original-stroke-width") || "1");
                            const arrowSize = Math.max(8, strokeWidth * 1.5);
                            addDistanceBasedArrow(linkElement as any, arrowSize);
                        });
                        // 选中状态下保持原有样式，只有原本有边框的才保持边框
                        d3.selectAll(`.stage-${this.selection.from}, .stage-${this.selection.to}`).each((d, i, nodes) => {
                            const rect = d3.select(nodes[i]);
                            const stage = rect.datum() as StageDatum;
                            const group = STAGE_GROUP_MAP[stage.stage];
                            if (group === 'Data-oriented' || group === 'Model-oriented') {
                                rect.attr("stroke", "#666666").attr("stroke-width", 5).attr("stroke-dasharray", group === 'Model-oriented' ? "8" : "none");
                            } else {
                                rect.attr("stroke", "none").attr("stroke-width", 0);
                            }
                        });
                    } else if (this.selection.type === 'stage') {
                        d3.selectAll(".flow-link").attr("opacity", 0.05);
                        const highlightedLinks = d3.selectAll(`.link-from-${this.selection.stage}, .link-to-${this.selection.stage}`).attr("opacity", 0.9);
                        // 为选中的stage相关的flow添加箭头
                        highlightedLinks.each(function () {
                            const linkElement = d3.select(this);
                            const strokeWidth = parseFloat(linkElement.attr("data-original-stroke-width") || "1");
                            const arrowSize = Math.max(8, strokeWidth * 1.5);
                            addDistanceBasedArrow(linkElement as any, arrowSize);
                        });
                        // 选中状态下保持原有样式，只有原本有边框的才保持边框
                        d3.selectAll(`.stage-${this.selection.stage}`).each((d, i, nodes) => {
                            const rect = d3.select(nodes[i]);
                            const stage = rect.datum() as StageDatum;
                            const group = STAGE_GROUP_MAP[stage.stage];
                            if (group === 'Data-oriented' || group === 'Model-oriented') {
                                rect.attr("stroke", "#666666").attr("stroke-width", 5).attr("stroke-dasharray", group === 'Model-oriented' ? "8" : "none");
                            } else {
                                rect.attr("stroke", "none").attr("stroke-width", 0);
                            }
                        });
                    }
                }
                // tooltip
                const tooltip = document.getElementById('galaxy-tooltip');
                tooltip!.style.display = 'none';
            })
            .on("pointerup", (event, d) => {
                if (isDragging) return;

                // 如果当前已经选中了这个stage，则取消选中
                if (this.selection && this.selection.type === 'stage' && this.selection.stage === d.stage) {
                    this.selection = null;
                    // 清除全局选中状态（按tab隔离）
                    const tabId = this.getTabId();
                    const flowSelectionKey = `_galaxyFlowSelection_${tabId}`;
                    const stageSelectionKey = `_galaxyStageSelection_${tabId}`;
                    (window as any)[stageSelectionKey] = null;
                    (window as any)[flowSelectionKey] = null;
                    this.saveFilterState();
                    // 避免重复渲染，只在状态真正改变时渲染
                    this.render();
                    window.dispatchEvent(new CustomEvent('galaxy-selection-cleared', { detail: { tabId: this.getTabId() } }));
                } else {
                    // 选中新的stage
                    this.selection = { type: 'stage', stage: d.stage };
                    // 设置全局选中状态（按tab隔离）
                    const tabId = this.getTabId();
                    const flowSelectionKey = `_galaxyFlowSelection_${tabId}`;
                    const stageSelectionKey = `_galaxyStageSelection_${tabId}`;
                    (window as any)[stageSelectionKey] = d.stage;
                    (window as any)[flowSelectionKey] = null;
                    this.saveFilterState();
                    // 避免重复渲染，只在状态真正改变时渲染
                    this.render();
                    window.dispatchEvent(new CustomEvent('galaxy-stage-selected', { detail: { stage: d.stage, tabId: this.getTabId() } }));
                }
            })
            .call(drag);
        // === END block rect ===

        // 统一收集所有实际渲染的 flow，并计算线宽比例尺
        const renderedFlows: { from: string, to: string, count: number }[] = [];
        transitions.forEach((count, key) => {
            const [from, to] = key.split("->");
            if (from === 'None' || to === 'None' || from === to) return;
            if (!stageMap.has(from) || !stageMap.has(to)) return; // 只渲染可见的
            renderedFlows.push({ from, to, count });
        });
        // const renderedFlowCounts = renderedFlows.map(f => f.count);

        // --- legend 渲染到底部 div ---
        this.legendDiv.innerHTML = '';

        // 按组分类，保持原有顺序
        const processGroups = () => {
            const allStages = this.stageData.filter(d => d.count > 0);
            const groups: Record<string, typeof this.stageData> = {
                'Environment': [],
                'Data-oriented': [],
                'Model-oriented': [],
                'Data export': [],
                'Other': []
            };

            allStages.forEach(stage => {
                // 过滤掉 Commented (10) 和 Other (12)，不在 legend 中显示
                if (stage.stage === '10' || stage.stage === '12') {
                    return;
                }
                const group = STAGE_GROUP_MAP[stage.stage] || 'Other';
                if (groups[group]) {
                    groups[group].push(stage);
                }
            });

            return groups;
        };

        const processedGroups = processGroups();

        // 创建主容器
        const legendContainer = document.createElement('div');
        legendContainer.style.display = 'flex';
        legendContainer.style.flexDirection = 'column';
        legendContainer.style.width = '100%';
        legendContainer.style.minWidth = '0'; // 允许容器收缩
        legendContainer.style.gap = '2px'; // 进一步减少垂直间隔

        // 创建单个组件的函数
        const createGroupBox = (groupName: string, stages: typeof this.stageData) => {
            if (stages.length === 0) return null;

            const groupBox = document.createElement('div');

            // 只有 Data-oriented 和 Model-oriented 有边框
            const shouldHaveBox = groupName === 'Data-oriented' || groupName === 'Model-oriented';
            if (shouldHaveBox) {
                groupBox.style.border = '1px solid #ddd';
                groupBox.style.borderRadius = '4px';
                groupBox.style.padding = '6px'; // 减少内边距
                groupBox.style.width = 'fit-content'; // 根据内容自适应宽度
                groupBox.style.height = 'auto'; // 根据内容自适应高度
                groupBox.style.minHeight = 'fit-content'; // 最小高度适应内容
                // groupBox.style.backgroundColor = '#f9f9f9';
                // Model-oriented 使用虚线边框
                if (groupName === 'Model-oriented') {
                    groupBox.style.borderStyle = 'dashed';
                }
            }
            groupBox.style.marginBottom = '1px'; // 进一步减少group之间的间隔

            // 组标题 - 只有 Data-oriented 和 Model-oriented 显示标题
            if (shouldHaveBox) {
                const groupTitle = document.createElement('div');
                groupTitle.style.fontSize = '12px';
                groupTitle.style.fontWeight = '600';
                groupTitle.style.color = '#555';
                groupTitle.style.marginBottom = '4px';
                groupTitle.style.opacity = '1';
                groupTitle.textContent = groupName;
                groupBox.appendChild(groupTitle);
            }

            // 组内容 - Data-oriented 和 Model-oriented 使用单列布局
            const groupContent = document.createElement('div');
            if (shouldHaveBox) {
                // 单列布局
                groupContent.style.display = 'flex';
                groupContent.style.flexDirection = 'column';
                groupContent.style.gap = '2px';

                stages.forEach((d) => {
                    const item = document.createElement('div');
                    item.style.display = 'flex';
                    item.style.alignItems = 'center';
                    // item.style.cursor = 'pointer';
                    item.style.padding = '1px 4px';
                    item.style.borderRadius = '2px';

                    const isStageHidden = this.hiddenStages.has(d.stage);
                    const colorBox = document.createElement('span');
                    colorBox.style.display = 'inline-block';
                    colorBox.style.width = '8px';
                    colorBox.style.height = '10px';
                    colorBox.style.borderRadius = '2px'; // 添加圆角
                    colorBox.style.background = this.colorMap.get(d.stage) || '#ccc';
                    colorBox.style.marginRight = '6px';
                    colorBox.style.opacity = isStageHidden ? '0.3' : '1';

                    // 为Data-oriented和Model-oriented添加border
                    const group = STAGE_GROUP_MAP[d.stage];
                    if (group === 'Data-oriented' || group === 'Model-oriented') {
                        colorBox.style.border = '1.5px solid #666666';
                        if (group === 'Model-oriented') {
                            colorBox.style.borderStyle = 'dashed';
                        }
                    }

                    const label = document.createElement('span');
                    label.style.fontSize = '12px';
                    label.textContent = LABEL_MAP[d.stage] ?? d.stage;
                    label.style.opacity = isStageHidden ? '0.3' : '1';

                    item.appendChild(colorBox);
                    item.appendChild(label);

                    // 点击切换显示/隐藏
                    /*
                    item.onclick = () => {
                        if (isStageHidden) {
                            this.hiddenStages.delete(d.stage);
                        } else {
                            this.hiddenStages.add(d.stage);
                        }
                        // 每次变更后派发事件
                        window.dispatchEvent(new CustomEvent('galaxy-hidden-stages-changed', {
                            detail: { hiddenStages: Array.from(this.hiddenStages) }
                        }));
                        this.saveFilterState();
                        this.render();
                    };
                    */

                    groupContent.appendChild(item);
                });
            } else if (groupName === 'Other') {
                // Other 组：单列布局（因为 Commented 和 Other 不在 legend 中显示）
                groupContent.style.display = 'flex';
                groupContent.style.flexDirection = 'column';
                groupContent.style.gap = '2px';

                stages.forEach((d) => {
                    const item = document.createElement('div');
                    item.style.display = 'flex';
                    item.style.alignItems = 'center';
                    // item.style.cursor = 'pointer';
                    item.style.padding = '1px 4px';
                    item.style.borderRadius = '2px';

                    const isStageHidden = this.hiddenStages.has(d.stage);
                    const colorBox = document.createElement('span');
                    colorBox.style.display = 'inline-block';
                    colorBox.style.width = '8px';
                    colorBox.style.height = '10px';
                    colorBox.style.borderRadius = '2px'; // 添加圆角
                    colorBox.style.background = this.colorMap.get(d.stage) || '#ccc';
                    colorBox.style.marginRight = '6px';
                    colorBox.style.opacity = isStageHidden ? '0.3' : '1';

                    // 为Data-oriented和Model-oriented添加border
                    const group = STAGE_GROUP_MAP[d.stage];
                    if (group === 'Data-oriented' || group === 'Model-oriented') {
                        colorBox.style.border = '1.5px solid #666666';
                        if (group === 'Model-oriented') {
                            colorBox.style.borderStyle = 'dashed';
                        }
                    }

                    const label = document.createElement('span');
                    label.style.fontSize = '12px';
                    label.textContent = LABEL_MAP[d.stage] ?? d.stage;
                    label.style.opacity = isStageHidden ? '0.3' : '1';

                    item.appendChild(colorBox);
                    item.appendChild(label);

                    // 点击切换显示/隐藏
                    /*
                    item.onclick = () => {
                        if (isStageHidden) {
                            this.hiddenStages.delete(d.stage);
                        } else {
                            this.hiddenStages.add(d.stage);
                        }
                        // 每次变更后派发事件
                        window.dispatchEvent(new CustomEvent('galaxy-hidden-stages-changed', {
                            detail: { hiddenStages: Array.from(this.hiddenStages) }
                        }));
                        this.saveFilterState();
                        this.render();
                    };
                    */

                    groupContent.appendChild(item);
                });
            } else {
                // 单列布局
                groupContent.style.display = 'flex';
                groupContent.style.flexDirection = 'column';
                groupContent.style.gap = '2px';

                stages.forEach((d) => {
                    const item = document.createElement('div');
                    item.style.display = 'flex';
                    item.style.alignItems = 'center';
                    // item.style.cursor = 'pointer';
                    item.style.padding = '1px 4px';
                    item.style.borderRadius = '2px';

                    const isStageHidden = this.hiddenStages.has(d.stage);
                    const colorBox = document.createElement('span');
                    colorBox.style.display = 'inline-block';
                    colorBox.style.width = '8px';
                    colorBox.style.height = '10px';
                    colorBox.style.borderRadius = '2px'; // 添加圆角
                    colorBox.style.background = this.colorMap.get(d.stage) || '#ccc';
                    colorBox.style.marginRight = '6px';
                    colorBox.style.opacity = isStageHidden ? '0.3' : '1';

                    // 为Data-oriented和Model-oriented添加border
                    const group = STAGE_GROUP_MAP[d.stage];
                    if (group === 'Data-oriented' || group === 'Model-oriented') {
                        colorBox.style.border = '1.5px solid #666666';
                        if (group === 'Model-oriented') {
                            colorBox.style.borderStyle = 'dashed';
                        }
                    }

                    const label = document.createElement('span');
                    label.style.fontSize = '12px';
                    label.textContent = LABEL_MAP[d.stage] ?? d.stage;
                    label.style.opacity = isStageHidden ? '0.3' : '1';

                    item.appendChild(colorBox);
                    item.appendChild(label);

                    // 点击切换显示/隐藏
                    /*
                    item.onclick = () => {
                        if (isStageHidden) {
                            this.hiddenStages.delete(d.stage);
                        } else {
                            this.hiddenStages.add(d.stage);
                        }
                        // 每次变更后派发事件
                        window.dispatchEvent(new CustomEvent('galaxy-hidden-stages-changed', {
                            detail: { hiddenStages: Array.from(this.hiddenStages) }
                        }));
                        this.saveFilterState();
                        this.render();
                    };
                    */

                    groupContent.appendChild(item);
                });
            }

            groupBox.appendChild(groupContent);
            return groupBox;
        };

        // 创建Data-oriented和Model-oriented的容器，让它们左右并排
        const dataGroup = createGroupBox('Data-oriented', processedGroups['Data-oriented'] || []);
        const modelGroup = createGroupBox('Model-oriented', processedGroups['Model-oriented'] || []);

        // 检查Data-oriented和Model-oriented是否存在
        const hasDataGroup = dataGroup !== null;
        const hasModelGroup = modelGroup !== null;

        if (hasDataGroup && hasModelGroup) {
            // 两个都存在，创建左右并排的容器
            const dataModelContainer = document.createElement('div');
            dataModelContainer.style.display = 'flex';
            dataModelContainer.style.gap = '12px';
            dataModelContainer.style.marginBottom = '1px';
            dataModelContainer.style.width = '100%';
            dataModelContainer.style.minWidth = '0';
            dataModelContainer.style.alignItems = 'flex-start';

            dataGroup!.style.flex = '1';
            dataGroup!.style.height = 'auto';
            dataModelContainer.appendChild(dataGroup!);

            modelGroup!.style.flex = '1';
            modelGroup!.style.height = 'auto';
            dataModelContainer.appendChild(modelGroup!);

            legendContainer.appendChild(dataModelContainer);
        } else if (hasDataGroup || hasModelGroup) {
            // 只有一个存在，创建左右布局的容器
            const singleContainer = document.createElement('div');
            singleContainer.style.display = 'flex';
            singleContainer.style.gap = '12px';
            singleContainer.style.marginBottom = '1px';
            singleContainer.style.width = '100%';
            singleContainer.style.alignItems = 'flex-start';

            const singleGroup = hasDataGroup ? dataGroup! : modelGroup!;
            singleGroup.style.width = 'fit-content';
            singleGroup.style.height = 'auto';
            singleContainer.appendChild(singleGroup);

            legendContainer.appendChild(singleContainer);
        }
        // 如果两个都不存在，不添加任何容器

        // 创建Environment和Data export的组合组
        const envStages = processedGroups['Environment'] || [];
        const exportStages = processedGroups['Data export'] || [];
        const combinedStages = [...envStages, ...exportStages];

        if (combinedStages.length > 0) {
            // 创建组合组
            const combinedGroup = document.createElement('div');
            combinedGroup.style.display = 'flex';
            combinedGroup.style.flexDirection = 'column';
            combinedGroup.style.gap = '2px';
            combinedGroup.style.marginBottom = '1px';

            // 添加Environment部分
            if (envStages.length > 0) {
                const envSection = document.createElement('div');
                envSection.style.display = 'flex';
                envSection.style.flexDirection = 'column';
                envSection.style.gap = '2px';

                envStages.forEach((d) => {
                    const item = document.createElement('div');
                    item.style.display = 'flex';
                    item.style.alignItems = 'center';
                    item.style.padding = '1px 4px';
                    item.style.borderRadius = '2px';

                    const isStageHidden = this.hiddenStages.has(d.stage);
                    const colorBox = document.createElement('span');
                    colorBox.style.display = 'inline-block';
                    colorBox.style.width = '8px';
                    colorBox.style.height = '10px';
                    colorBox.style.borderRadius = '2px';
                    colorBox.style.background = this.colorMap.get(d.stage) || '#ccc';
                    colorBox.style.marginRight = '6px';
                    colorBox.style.opacity = isStageHidden ? '0.3' : '1';

                    const label = document.createElement('span');
                    label.style.fontSize = '12px';
                    label.textContent = LABEL_MAP[d.stage] ?? d.stage;
                    label.style.opacity = isStageHidden ? '0.3' : '1';

                    item.appendChild(colorBox);
                    item.appendChild(label);
                    envSection.appendChild(item);
                });

                combinedGroup.appendChild(envSection);
            }

            // 添加Data export部分
            if (exportStages.length > 0) {
                const exportSection = document.createElement('div');
                exportSection.style.display = 'flex';
                exportSection.style.flexDirection = 'column';
                exportSection.style.gap = '2px';

                exportStages.forEach((d) => {
                    const item = document.createElement('div');
                    item.style.display = 'flex';
                    item.style.alignItems = 'center';
                    item.style.padding = '1px 4px';
                    item.style.borderRadius = '2px';

                    const isStageHidden = this.hiddenStages.has(d.stage);
                    const colorBox = document.createElement('span');
                    colorBox.style.display = 'inline-block';
                    colorBox.style.width = '8px';
                    colorBox.style.height = '10px';
                    colorBox.style.borderRadius = '2px';
                    colorBox.style.background = this.colorMap.get(d.stage) || '#ccc';
                    colorBox.style.marginRight = '6px';
                    colorBox.style.opacity = isStageHidden ? '0.3' : '1';

                    const label = document.createElement('span');
                    label.style.fontSize = '12px';
                    label.textContent = LABEL_MAP[d.stage] ?? d.stage;
                    label.style.opacity = isStageHidden ? '0.3' : '1';

                    item.appendChild(colorBox);
                    item.appendChild(label);
                    exportSection.appendChild(item);
                });

                combinedGroup.appendChild(exportSection);
            }

            // 根据Data-oriented和Model-oriented的存在情况决定放置位置
            if (hasDataGroup && hasModelGroup) {
                // 两个都存在，使用原有的逻辑
                const dataStageCount = processedGroups['Data-oriented'] ? processedGroups['Data-oriented'].length : 0;
                const modelStageCount = processedGroups['Model-oriented'] ? processedGroups['Model-oriented'].length : 0;

                if (dataStageCount < modelStageCount) {
                    // Data-oriented的stage数量较少，将组合组放在Data-oriented框外面
                    dataGroup!.style.position = 'relative';
                    combinedGroup.style.position = 'absolute';
                    combinedGroup.style.top = '100%';
                    combinedGroup.style.left = '0';
                    combinedGroup.style.marginTop = '4px';
                    dataGroup!.appendChild(combinedGroup);
                } else if (modelStageCount < dataStageCount) {
                    // Model-oriented的stage数量较少，将组合组放在Model-oriented框外面
                    modelGroup!.style.position = 'relative';
                    combinedGroup.style.position = 'absolute';
                    combinedGroup.style.top = '100%';
                    combinedGroup.style.left = '0';
                    combinedGroup.style.marginTop = '4px';
                    modelGroup!.appendChild(combinedGroup);
                } else {
                    // 两个框的stage数量相等，分别放置Environment和Data export
                    // 创建Environment组
                    if (envStages.length > 0) {
                        const envGroup = document.createElement('div');
                        envGroup.style.display = 'flex';
                        envGroup.style.flexDirection = 'column';
                        envGroup.style.gap = '2px';
                        envGroup.style.marginBottom = '1px';

                        envStages.forEach((d) => {
                            const item = document.createElement('div');
                            item.style.display = 'flex';
                            item.style.alignItems = 'center';
                            item.style.padding = '1px 4px';
                            item.style.borderRadius = '2px';

                            const isStageHidden = this.hiddenStages.has(d.stage);
                            const colorBox = document.createElement('span');
                            colorBox.style.display = 'inline-block';
                            colorBox.style.width = '8px';
                            colorBox.style.height = '10px';
                            colorBox.style.borderRadius = '2px';
                            colorBox.style.background = this.colorMap.get(d.stage) || '#ccc';
                            colorBox.style.marginRight = '6px';
                            colorBox.style.opacity = isStageHidden ? '0.3' : '1';

                            const label = document.createElement('span');
                            label.style.fontSize = '12px';
                            label.textContent = LABEL_MAP[d.stage] ?? d.stage;
                            label.style.opacity = isStageHidden ? '0.3' : '1';

                            item.appendChild(colorBox);
                            item.appendChild(label);
                            envGroup.appendChild(item);
                        });

                        // 将Environment组放在Data-oriented框外面
                        dataGroup!.style.position = 'relative';
                        envGroup.style.position = 'absolute';
                        envGroup.style.top = '100%';
                        envGroup.style.left = '0';
                        envGroup.style.marginTop = '4px';
                        dataGroup!.appendChild(envGroup);
                    }

                    // 创建Data export组
                    if (exportStages.length > 0) {
                        const exportGroup = document.createElement('div');
                        exportGroup.style.display = 'flex';
                        exportGroup.style.flexDirection = 'column';
                        exportGroup.style.gap = '2px';
                        exportGroup.style.marginBottom = '1px';

                        exportStages.forEach((d) => {
                            const item = document.createElement('div');
                            item.style.display = 'flex';
                            item.style.alignItems = 'center';
                            item.style.padding = '1px 4px';
                            item.style.borderRadius = '2px';

                            const isStageHidden = this.hiddenStages.has(d.stage);
                            const colorBox = document.createElement('span');
                            colorBox.style.display = 'inline-block';
                            colorBox.style.width = '8px';
                            colorBox.style.height = '10px';
                            colorBox.style.borderRadius = '2px';
                            colorBox.style.background = this.colorMap.get(d.stage) || '#ccc';
                            colorBox.style.marginRight = '6px';
                            colorBox.style.opacity = isStageHidden ? '0.3' : '1';

                            const label = document.createElement('span');
                            label.style.fontSize = '12px';
                            label.textContent = LABEL_MAP[d.stage] ?? d.stage;
                            label.style.opacity = isStageHidden ? '0.3' : '1';

                            item.appendChild(colorBox);
                            item.appendChild(label);
                            exportGroup.appendChild(item);
                        });

                        // 将Data export组放在Model-oriented框外面
                        modelGroup!.style.position = 'relative';
                        exportGroup.style.position = 'absolute';
                        exportGroup.style.top = '100%';
                        exportGroup.style.left = '0';
                        exportGroup.style.marginTop = '4px';
                        modelGroup!.appendChild(exportGroup);
                    }
                }
            } else if (hasDataGroup || hasModelGroup) {
                // 只有一个存在，将组合组放在容器的右边
                const singleContainer = legendContainer.lastElementChild as HTMLElement;
                if (singleContainer) {
                    combinedGroup.style.width = 'fit-content';
                    combinedGroup.style.height = 'auto';
                    singleContainer.appendChild(combinedGroup);
                }
            } else {
                // 两个都不存在，直接添加到主容器
                legendContainer.appendChild(combinedGroup);
            }
        }

        // 添加Other组
        const otherGroup = createGroupBox('Other', processedGroups['Other'] || []);
        if (otherGroup) {
            legendContainer.appendChild(otherGroup);
        }

        this.legendDiv.appendChild(legendContainer);
        this.legendDiv.style.border = '';

        // === legend SVG 渲染（width legend 和 size legend）放到所有背景之后 ===
        // 注释掉 stage 和 transition frequency 的 legend
        /*
        if (renderedFlowCounts.length > 0) {
            const min = Math.min(...renderedFlowCounts);
            const max = Math.max(...renderedFlowCounts);
            // 采样点：如果样本数量少于5个，就画实际数量
            let samples: number[];
            if (renderedFlowCounts.length < 5) {
                // 如果样本数量少于5个，就画实际数量
                samples = [...renderedFlowCounts].sort((a, b) => a - b);
            } else {
                // 如果样本数量大于等于5个，采样5个点
                samples = [
                    min,
                    Math.round(min + 0.25 * (max - min)),
                    Math.round(min + 0.5 * (max - min)),
                    Math.round(min + 0.75 * (max - min)),
                    max
                ];
            }
            const uniqSamples = Array.from(new Set(samples));
            const svgW = 220;

                    // legend始终画在SVG底部区域，且不与背景重叠
        const minLegendY = svgHeight - legendAreaHeight + 50; // 调整位置，给flow chart留更多空间
        const bottomY = minLegendY;

            // 统一声明legend相关变量
            const stageCounts = this.stageData.map(d => d.count);
            const minCount = Math.min(...stageCounts);
            const maxCount = Math.max(...stageCounts);

            // width legend - 更优雅的布局
            const legendG = svg.append("g").attr("transform", `translate(0, ${bottomY})`);

            // 添加标题，居中对齐到sample区域
            legendG.append("text")
                .attr("x", 28 + svgW / 2) // 居中对齐到sample区域
                .attr("y", 15)
                .attr("text-anchor", "middle")
                .attr("font-size", "20")
                .attr("font-weight", "600")
                .attr("fill", "#555")
                .text("Flow Frequency");

            // 绘制宽度示例线条
            const lineY = 100; // 增加标题和sample之间的距离
            uniqSamples.forEach((count, i) => {
                const x = 28 + i * ((svgW - 56) / (uniqSamples.length - 1));
                const w = strokeScale(count);

                // 绘制方形来展示线宽，使用和flow chart一样的尺寸
                legendG.append("rect")
                    .attr("x", x - w / 2)
                    .attr("y", lineY - 60) // 底部对齐到lineY
                    .attr("width", w)
                    .attr("height", 60) // 使用固定高度，和flow chart保持一致
                    .attr("fill", "#666")
                    .attr("opacity", 0.8);

            });

            // 在sample同一排的左右两边添加具体数值标签
            legendG.append("text")
                .attr("x", 10)
                .attr("y", lineY - 30) // 垂直居中对齐到柱子中心
                .attr("text-anchor", "start")
                .attr("font-size", "15")
                .attr("fill", "#666")
                .text(min.toLocaleString());

            // 只有当有多个柱子时才显示右边的label
            if (uniqSamples.length > 1) {
                legendG.append("text")
                    .attr("x", 28 + svgW - 8)
                    .attr("y", lineY - 30) // 垂直居中对齐到柱子中心
                    .attr("text-anchor", "end")
                    .attr("font-size", "15")
                    .attr("fill", "#666")
                    .text(max.toLocaleString());
            }

            // === 添加 stage rect size 的 legend（矩形高度表示count）===
            // size legend - 固定宽度，高度表示count
            const sizeLegendG = svg.append("g").attr("transform", `translate(260, ${bottomY})`);

            // 绘制一个不填充的矩形，从顶部到延伸线的距离代表高度
            const rectWidth = 60; // 矩形宽度，和flow chart保持一致
            const rectHeight = sizeScale(maxCount); // 矩形高度，使用最大count对应的高度
            const rectX = 30; // 矩形x位置
            const rectY = 25; // 矩形y位置，底部和flow frequency对齐

            // 添加标题，居中对齐到sample区域
            sizeLegendG.append("text")
                .attr("x", rectX + rectWidth / 2) // 居中对齐到矩形区域
                .attr("y", 15)
                .attr("text-anchor", "middle")
                .attr("font-size", "20")
                .attr("font-weight", "600")
                .attr("fill", "#555")
                .text("Stage Frequency");

            // 绘制不填充的矩形
            sizeLegendG.append("rect")
                .attr("x", rectX)
                .attr("y", rectY)
                .attr("width", rectWidth)
                .attr("height", rectHeight)
                .attr("rx", 6) // 添加圆角
                .attr("ry", 6) // 添加圆角
                .attr("fill", "none")
                .attr("stroke", "#666")
                .attr("stroke-width", 2)
                .attr("opacity", 0.8);

            // 采样3个点：min, (min+max)/2, max
            const stageSamples = [minCount, Math.round((minCount + maxCount) / 2), maxCount];

            stageSamples.forEach((count, i) => {
                // 计算从顶部到延伸线的距离，这个距离代表高度
                // 使用和flow chart一样的sizeScale计算高度
                const actualHeight = sizeScale(count);
                const lineY = rectY + actualHeight;

                // 绘制水平线
                sizeLegendG.append("line")
                    .attr("x1", rectX)
                    .attr("y1", lineY)
                    .attr("x2", rectX + rectWidth)
                    .attr("y2", lineY)
                    .attr("stroke", "#666")
                    .attr("stroke-width", 1)
                    .attr("opacity", 0.8);

                // 添加延伸线到标签
                const labelX = rectX + rectWidth + 15;

                // 水平延伸线
                sizeLegendG.append("line")
                    .attr("x1", rectX + rectWidth)
                    .attr("y1", lineY)
                    .attr("x2", labelX)
                    .attr("y2", lineY)
                    .attr("stroke", "#666")
                    .attr("stroke-width", 1)
                    .attr("stroke-dasharray", "2,2")
                    .attr("opacity", 0.6);

                // 添加数值标签
                sizeLegendG.append("text")
                    .attr("x", labelX + 5)
                    .attr("y", lineY + 4)
                    .attr("font-size", "15")
                    .attr("fill", "#666")
                    .attr("text-anchor", "start")
                    .text(count.toLocaleString());
            });
        }
        */
        // === END legend SVG 渲染 ===

        // 保证 colorMap 有所有 stage 的颜色
        const palette = d3.schemeSet3;
        this.stageData.forEach((d, i) => {
            if (!this.colorMap.has(d.stage)) {
                this.colorMap.set(d.stage, palette[i % palette.length]);
            }
        });



        // 根据selection状态应用高亮效果
        if (this.selection) {
            if (this.selection.type === 'stage') {
                // 高亮选中的stage
                d3.selectAll(".flow-link").attr("opacity", 0.05);
                const highlightedLinks = d3.selectAll(`.link-from-${this.selection.stage}, .link-to-${this.selection.stage}`).attr("opacity", 0.9);

                // 为选中的stage相关的flow添加箭头
                highlightedLinks.each(function () {
                    const linkElement = d3.select(this);
                    const strokeWidth = parseFloat(linkElement.attr("data-original-stroke-width") || "1");
                    const arrowSize = Math.max(8, strokeWidth * 1.5);
                    addDistanceBasedArrow(linkElement as any, arrowSize);
                });

                // 选中状态下保持原有样式，只有原本有边框的才保持边框
                d3.selectAll(`.stage-${this.selection.stage}`).each((d, i, nodes) => {
                    const rect = d3.select(nodes[i]);
                    const stage = rect.datum() as StageDatum;
                    const group = STAGE_GROUP_MAP[stage.stage];
                    if (group === 'Data-oriented' || group === 'Model-oriented') {
                        rect.attr("stroke", "#666666").attr("stroke-width", 5).attr("stroke-dasharray", group === 'Model-oriented' ? "8" : "none");
                    } else {
                        rect.attr("stroke", "none").attr("stroke-width", 0);
                    }
                });
            } else if (this.selection.type === 'flow') {
                // 高亮选中的flow
                d3.selectAll(".flow-link").attr("opacity", 0.05);
                const highlightedLinks = d3.selectAll(`.link-from-${this.selection.from}.link-to-${this.selection.to}`).attr("opacity", 1);

                // 为选中的flow添加箭头
                highlightedLinks.each(function () {
                    const linkElement = d3.select(this);
                    const strokeWidth = parseFloat(linkElement.attr("data-original-stroke-width") || "1");
                    const arrowSize = Math.max(8, strokeWidth * 1.5);
                    addDistanceBasedArrow(linkElement as any, arrowSize);
                });

                // 选中状态下保持原有样式，只有原本有边框的才保持边框
                d3.selectAll(`.stage-${this.selection.from}, .stage-${this.selection.to}`).each((d, i, nodes) => {
                    const rect = d3.select(nodes[i]);
                    const stage = rect.datum() as StageDatum;
                    const group = STAGE_GROUP_MAP[stage.stage];
                    if (group === 'Data-oriented' || group === 'Model-oriented') {
                        rect.attr("stroke", "#666666").attr("stroke-width", 5).attr("stroke-dasharray", group === 'Model-oriented' ? "8" : "none");
                    } else {
                        rect.attr("stroke", "none").attr("stroke-width", 0);
                    }
                });
            }
        } else {
            // 没有选中状态时，恢复默认的border样式
            d3.selectAll(`.stage-rect`).each((d, i, nodes) => {
                const rect = d3.select(nodes[i]);
                const stage = rect.datum() as StageDatum;
                const group = STAGE_GROUP_MAP[stage.stage];
                if (group === 'Data-oriented' || group === 'Model-oriented') {
                    rect.attr("stroke", "#666666").attr("stroke-width", 5).attr("stroke-dasharray", group === 'Model-oriented' ? "8" : "none");
                } else {
                    rect.attr("stroke", "none").attr("stroke-width", 0);
                }
            });
        }

        // 选中状态下不触发hover事件，避免minimap高亮

        // 获取top stages和top transitions（过滤掉隐藏的stages）
        const stageEntries = Array.from(stageStats.entries())
            .filter(([stage]) => !this.hiddenStages.has(stage) && stage !== "None")
            .sort((a, b) => b[1].count - a[1].count);

        // 获取数量最多的stage（可能有多个数量相同的）
        const maxStageCount = stageEntries.length > 0 ? stageEntries[0][1].count : 0;
        const topStages = stageEntries
            .filter(([stage, stats]) => stats.count === maxStageCount)
            .map(([stage, stats]) => [stage, stats.count] as [string, number]);

        const transitionEntries = Array.from(transitions.entries())
            .filter(([transition]) => {
                const [from, to] = transition.split("->");
                return !this.hiddenStages.has(from) && !this.hiddenStages.has(to);
            })
            .sort((a, b) => b[1] - a[1]);

        // 获取数量最多的transition（可能有多个数量相同的）
        const maxTransitionCount = transitionEntries.length > 0 ? transitionEntries[0][1] : 0;
        const topTransitions = transitionEntries
            .filter(([transition, count]) => count === maxTransitionCount)
            .map(([transition, count]) => [transition.replace('->', ' → '), count] as [string, number]);

        // 派发top stages和top transitions给MatrixWidget
        window.dispatchEvent(new CustomEvent('galaxy-top-stats-updated', {
            detail: {
                topStages: topStages.length > 0 ? topStages : undefined,
                topTransitions: topTransitions.length > 0 ? topTransitions : undefined
            }
        }));
    }



    dispose(): void {
        if (this._resizeObserver) {
            this._resizeObserver.disconnect();
            this._resizeObserver = null;
        }
        if (this._renderTimeout) {
            clearTimeout(this._renderTimeout);
            this._renderTimeout = null;
        }

        // 移除事件监听器
        Object.keys(this._eventHandlers).forEach(eventName => {
            window.removeEventListener(eventName, this._eventHandlers[eventName]);
        });
        this._eventHandlers = {};

        super.dispose();
    }

    onAfterAttach(msg: any): void {
        // 恢复之前的筛选状态
        this.restoreFilterState();

        // 先断开旧的 observer
        if (this._resizeObserver) {
            this._resizeObserver.disconnect();
            this._resizeObserver = null;
        }
        const svgElement = this.svg?.node();
        if (svgElement) {
            // 向上查找带有特定 class 的父元素
            let sidebarElem: HTMLElement = this.node;
            let el: HTMLElement | null = this.node;
            while (el) {
                if (
                    el.classList.contains('jp-SidePanel') ||
                    el.classList.contains('p-SidePanel') ||
                    el.classList.contains('jp-LeftArea') ||
                    el.classList.contains('jp-RightArea')
                ) {
                    sidebarElem = el;
                    break;
                }
                el = el.parentElement;
            }
            if (!sidebarElem) {
                sidebarElem = this.node.parentElement || this.node;
            }
            let lastWidth = sidebarElem.offsetWidth;
            const setSvgMarginBottom = () => {
                const sidebarWidth = sidebarElem.offsetWidth;
                if (sidebarWidth !== lastWidth) {
                    svgElement.style.marginBottom = Math.round(sidebarWidth) + 'px';
                    lastWidth = sidebarWidth;
                }
            };
            setSvgMarginBottom();
            this._resizeObserver = new ResizeObserver(setSvgMarginBottom);
            this._resizeObserver.observe(sidebarElem);
        }
        super.onAfterAttach?.(msg);
    }



    // 根据筛选结果更新数据并重渲染
    setData(data: Notebook[], colorMap: Map<string, string>) {
        this.data = data;
        this.colorMap = colorMap;



        // 保持当前的selection状态，不清除
        // this.selection = null;
        // 重新初始化 stageData 和 initialStageOrder：基于在所有notebook中的平均相对位置
        const stageNotebookPositions = new Map<string, number[]>(); // stage -> array of average positions in each notebook
        
        this.data.forEach((nb) => {
            const codeCells = [...nb.cells]
                .sort((a, b) => a.cellId - b.cellId)
                .filter((d) => d.cellType === 'code');
            
            if (codeCells.length === 0) return;
            
            // 计算这个notebook中每个stage的平均相对位置
            const stagePositionsInThisNotebook = new Map<string, number[]>();
            codeCells.forEach((cell, index) => {
                const stage = String(cell["1st-level label"] ?? "None");
                if (stage === "None") return;
                
                // 计算这个cell在notebook中的相对位置
                const relativePos = codeCells.length > 1 ? index / (codeCells.length - 1) : 0.5;
                
                if (!stagePositionsInThisNotebook.has(stage)) {
                    stagePositionsInThisNotebook.set(stage, []);
                }
                stagePositionsInThisNotebook.get(stage)!.push(relativePos);
            });
            
            // 计算每个stage在这个notebook中的平均位置，并添加到全局记录中
            stagePositionsInThisNotebook.forEach((positions, stage) => {
                const avgPosInThisNotebook = positions.reduce((sum, pos) => sum + pos, 0) / positions.length;
                
                if (!stageNotebookPositions.has(stage)) {
                    stageNotebookPositions.set(stage, []);
                }
                stageNotebookPositions.get(stage)!.push(avgPosInThisNotebook);
            });
        });
        
        // 计算每个stage在所有包含它的notebook中的最终平均相对位置
        const stageAvgPositions = new Map<string, { avgPos: number, notebookCount: number }>();
        stageNotebookPositions.forEach((notebookPositions, stage) => {
            const avgPos = notebookPositions.reduce((sum, pos) => sum + pos, 0) / notebookPositions.length;
            stageAvgPositions.set(stage, { avgPos, notebookCount: notebookPositions.length });
        });
        
        // 按平均相对位置排序stages，当相对位置相等时，参考overview中的排序
        const sortedStages = Array.from(stageAvgPositions.entries())
            .sort((a, b) => {
                // 首先按平均相对位置排序
                const positionDiff = a[1].avgPos - b[1].avgPos;
                if (Math.abs(positionDiff) > 1e-6) { // 如果位置不相等（允许浮点数精度误差）
                    return positionDiff;
                }
                
                // 如果位置相等，参考overview中的排序
                const aIndexInOverview = this.overviewStageOrder.indexOf(a[0]);
                const bIndexInOverview = this.overviewStageOrder.indexOf(b[0]);
                
                // 如果两个stage都在overview排序中，按overview顺序排列
                if (aIndexInOverview !== -1 && bIndexInOverview !== -1) {
                    return aIndexInOverview - bIndexInOverview;
                }
                
                // 如果只有一个在overview排序中，已存在的排在前面
                if (aIndexInOverview !== -1) return -1;
                if (bIndexInOverview !== -1) return 1;
                
                // 如果都不在overview排序中，按字典序排列
                return a[0].localeCompare(b[0]);
            })
            .map(([stage, data]) => ({ stage: String(stage), count: 0 }));
        
        this.stageData = sortedStages;
        this.initialStageOrder = this.stageData.map(d => d.stage);



        this.render();
    }



    // 获取当前tab ID
    private getTabId(): string {
        // 基于当前显示的内容生成唯一标识
        // 如果是notebook detail模式，使用notebook的ID
        if (this.data && this.data.length === 1 && (this.data[0] as any).globalIndex !== undefined) {
            return `notebook_${(this.data[0] as any).globalIndex}`;
        }
        // 如果是overview模式，使用overview标识
        return 'overview';
    }

    // 保存筛选状态到全局变量（按tab隔离）
    private saveFilterState() {
        const tabId = this.getTabId();
        const stateKey = `_galaxyLeftSidebarFilterState_${tabId}`;
        const flowSelectionKey = `_galaxyFlowSelection_${tabId}`;
        const stageSelectionKey = `_galaxyStageSelection_${tabId}`;

        // 保存到按tab隔离的全局变量
        if (this.selection) {
            if (this.selection.type === 'stage') {
                (window as any)[stageSelectionKey] = this.selection.stage;
                (window as any)[flowSelectionKey] = null;
            } else if (this.selection.type === 'flow') {
                (window as any)[flowSelectionKey] = { from: this.selection.from, to: this.selection.to };
                (window as any)[stageSelectionKey] = null;
            }
        } else {
            (window as any)[stageSelectionKey] = null;
            (window as any)[flowSelectionKey] = null;
        }

        // 保存到原有的状态对象
        (window as any)[stateKey] = {
            selection: this.selection,
            hiddenStages: Array.from(this.hiddenStages),
            stageData: this.stageData
        };
    }



    // 获取最频繁的stage和flow
    getMostFrequentStageAndFlow() {
        const mostFreqStage = this.stageData.reduce((max, current) =>
            current.count > max.count ? current : max, this.stageData[0]);

        // 计算最频繁的flow
        const transitions: Map<string, number> = new Map();
        this.data.forEach((nb) => {
            const cells = [...nb.cells]
                .sort((a, b) => a.cellId - b.cellId)
                .filter((d) => d.cellType === 'code');
            const stageSeq: string[] = [];
            cells.forEach((cell) => {
                const stage = String(cell["1st-level label"] ?? "None");
                if (stageSeq.length === 0 || stageSeq[stageSeq.length - 1] !== stage) {
                    stageSeq.push(stage);
                }
            });

            for (let i = 0; i < stageSeq.length - 1; i++) {
                const from = stageSeq[i];
                const to = stageSeq[i + 1];
                if (from !== "None" && to !== "None") {
                    const key = `${from}->${to}`;
                    transitions.set(key, (transitions.get(key) || 0) + 1);
                }
            }
        });

        let mostFreqFlow = { from: '', to: '', count: 0 };
        transitions.forEach((count, key) => {
            const [from, to] = key.split("->");
            if (count > mostFreqFlow.count) {
                mostFreqFlow = { from, to, count };
            }
        });

        return {
            mostFreqStage: mostFreqStage?.stage || '',
            mostFreqFlow: mostFreqFlow.from && mostFreqFlow.to ? `${mostFreqFlow.from}->${mostFreqFlow.to}` : ''
        };
    }

    // 从全局变量恢复筛选状态（按tab隔离）
    private restoreFilterState() {
        // 切换tab时隐藏所有tooltip
        const galaxyTooltip = document.getElementById('galaxy-tooltip');
        if (galaxyTooltip) {
            galaxyTooltip.style.display = 'none';
        }

        const tabId = this.getTabId();
        const stateKey = `_galaxyLeftSidebarFilterState_${tabId}`;
        const flowSelectionKey = `_galaxyFlowSelection_${tabId}`;
        const stageSelectionKey = `_galaxyStageSelection_${tabId}`;
        const savedState = (window as any)[stateKey];

        if (savedState) {
            this.selection = savedState.selection;
            this.hiddenStages = new Set(savedState.hiddenStages || ['10', '12']);
            if (savedState.stageData) {
                this.stageData = savedState.stageData;
            }

            // 恢复按tab隔离的全局变量
            if (this.selection) {
                if (this.selection.type === 'stage') {
                    (window as any)[stageSelectionKey] = this.selection.stage;
                    (window as any)[flowSelectionKey] = null;
                } else if (this.selection.type === 'flow') {
                    (window as any)[flowSelectionKey] = { from: this.selection.from, to: this.selection.to };
                    (window as any)[stageSelectionKey] = null;
                }
            } else {
                (window as any)[stageSelectionKey] = null;
                (window as any)[flowSelectionKey] = null;
            }

            // 恢复状态后重新渲染
            this.render();
        } else {
            // 如果没有保存的状态，使用默认状态（无选中状态）
            this.selection = null;
            this.hiddenStages = new Set(['10', '12']); // 默认隐藏的stages
            (window as any)[stageSelectionKey] = null;
            (window as any)[flowSelectionKey] = null;
            this.render();
        }
    }
}