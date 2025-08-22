import {
  ILayoutRestorer,
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
  ICommandPalette,
  ToolbarButton
} from '@jupyterlab/apputils';

import { IFileBrowserFactory, FileBrowser } from '@jupyterlab/filebrowser';
import { LeftSidebar } from './components/LeftSidebar';
import { SimpleNotebookListWidget } from './components/SimpleNotebookListWidget';
import { SimpleNotebookDetailWidget } from './components/SimpleNotebookDetailWidget';
import { SimpleInfoSidebar } from './components/SimpleInfoSidebar';

import { runIcon } from '@jupyterlab/ui-components';
import { colorMap as colorMapModule, initColorMap } from './components/colorMap';
import { MatrixWidget } from './components/MatrixWidget';
import { DetailSidebar } from './components/DetailSidebar';
import { NotebookDetailWidget } from './components/NotebookDetailWidget';
import { LabShell } from '@jupyterlab/application';
import { csvParse } from 'd3-dsv';
import { PostHogAnalytics } from './analytics/posthog-config';

// Get analytics instance
const analytics = PostHogAnalytics.getInstance();


// 从JSON文件名中提取competition编号
function extractCompetitionId(jsonPath: string): string | null {
  const match = jsonPath.match(/(\d+)_(predicted|reassigned)\.json$/);
  return match ? match[1] : null;
}

// 加载competition信息
async function loadCompetitionsData(baseDir?: string): Promise<{ [key: string]: { id: string; name: string; url: string; description?: string; category?: string; evaluation?: string; startDate?: string; endDate?: string } }> {
  try {
    const contentsManager = app?.serviceManager?.contents;
    if (!contentsManager) {
      console.warn('Contents manager not available for competitions loading');
      return {};
    }

    // 如果有baseDir，从指定目录加载
    if (baseDir) {
      const competitionPath = `${baseDir}/competition_data/competitions.json`;
      try {
        const model = await contentsManager.get(competitionPath, { type: 'file', format: 'text', content: true });
        const competitionsData = JSON.parse(model.content as string);
        
        // 转换为映射格式
        const competitionMap: { [key: string]: any } = {};
        competitionsData.forEach((comp: any) => {
          competitionMap[comp.id] = {
            id: comp.id,
            name: comp.name,
            url: comp.url,
            description: comp.description,
            category: comp.category,
            evaluation: comp.evaluation,
            startDate: comp.startDate,
            endDate: comp.endDate
          };
        });
        
        return competitionMap;
      } catch (fileError) {
        // Competition data not available in baseDir
      }
    }

    // 如果没有baseDir或加载失败，尝试从当前目录加载
    const jsonPaths = [
      './competition_data/competitions.json',
      'competition_data/competitions.json'
    ];

    for (const path of jsonPaths) {
      try {
        const model = await contentsManager.get(path, { type: 'file', format: 'text', content: true });
        const competitionsData = JSON.parse(model.content as string);
        
        // 转换为映射格式
        const competitionMap: { [key: string]: any } = {};
        competitionsData.forEach((comp: any) => {
          competitionMap[comp.id] = {
            id: comp.id,
            name: comp.name,
            url: comp.url,
            description: comp.description,
            category: comp.category,
            evaluation: comp.evaluation,
            startDate: comp.startDate,
            endDate: comp.endDate
          };
        });
        
        return competitionMap;
      } catch (fileError) {
        continue;
      }
    }

    console.warn('Could not load competitions.json, falling back to hardcoded data');
    return {};
  } catch (error) {
    console.warn('Error loading competitions data:', error);
    return {};
  }
}

// 根据competition ID获取competition信息
async function getCompetitionInfo(competitionId: string, baseDir?: string): Promise<{ id: string; name: string; url: string; description?: string; category?: string; evaluation?: string; startDate?: string; endDate?: string } | null> {
  try {
    const competitionMap = await loadCompetitionsData(baseDir);
    const info = competitionMap[competitionId];
    
    if (info) {
      return info;
    }
    
    // 如果从文件加载失败，使用硬编码的fallback数据
    const fallbackMap: { [key: string]: { name: string; url: string } } = {
      '18599': {
        name: 'M5 forecasting accuracy',
        url: 'https://www.kaggle.com/competitions/m5-forecasting-accuracy'
      },
      '50160': {
        name: 'Home Credit - Credit Risk Model Stability',
        url: 'https://www.kaggle.com/competitions/home-credit-credit-risk-model-stability'
      },
      '35332': {
        name: 'American Express',
        url: 'https://www.kaggle.com/competitions/amex-default-prediction'
      }
    };

    const fallbackInfo = fallbackMap[competitionId];
    return fallbackInfo ? { id: competitionId, ...fallbackInfo } : null;
  } catch (error) {
    console.warn('Error getting competition info:', error);
    return null;
  }
}

// 从JSON文件路径中提取基础目录
function extractBaseDir(jsonPath: string): string | null {
  // 移除文件名，获取目录路径
  const lastSlashIndex = jsonPath.lastIndexOf('/');
  if (lastSlashIndex === -1) {
    return null; // 没有目录分隔符，说明是根目录
  }
  return jsonPath.substring(0, lastSlashIndex);
}

// 加载TOC数据
async function loadTocData(competitionId: string, baseDir: string): Promise<any[]> {
  try {
    if (!baseDir) {
              return [];
    }

    const tocPath = `${baseDir}/toc_data/${competitionId}_toc.json`;
        const contentsManager = app?.serviceManager?.contents;

        if (!contentsManager) {
          console.warn('Contents manager not available for TOC loading');
          return [];
        }

    // 尝试加载TOC数据
    try {
      const model = await contentsManager.get(tocPath, { type: 'file', format: 'text', content: true });
      const tocData = JSON.parse(model.content as string);
      return tocData;
    } catch (fileError) {
      // TOC data not available
    }
    return [];
  } catch (error) {
            return [];
  }
}

// 加载Summary数据
async function loadSummaryData(competitionId: string, baseDir: string): Promise<any> {
  try {
    if (!baseDir) {
              return null;
    }

    const summaryPath = `${baseDir}/summary_data/${competitionId}_summarized.json`;
        const contentsManager = app?.serviceManager?.contents;

        if (!contentsManager) {
          console.warn('Contents manager not available for Summary loading');
          return null;
        }

    // 尝试加载Summary数据
    try {
      const model = await contentsManager.get(summaryPath, { type: 'file', format: 'text', content: true });
      const summaryData = JSON.parse(model.content as string);
      return summaryData;
    } catch (fileError) {
      // Summary data not available
    }
    return null;
  } catch (error) {
            return null;
  }
}

// 将TOC数据合并到notebook数据中
function mergeTocData(notebooks: any[], tocData: any[]): any[] {
  const tocMap = new Map();
  tocData.forEach(item => {
    tocMap.set(item.kernelVersionId, item.toc);
  });

  return notebooks.map(notebook => {
    const toc = tocMap.get(notebook.kernelVersionId);
    if (toc) {
      return { ...notebook, toc };
    } else {
              // No TOC found for notebook
    }
    return notebook;
  });
}

// 创建KernelVersionId到Title的映射
async function createKernelTitleMap(competitionId: string, baseDir: string): Promise<Map<string, { title: string; creationDate: string; totalLines: number; displayname?: string; url?: string }>> {
  try {
    if (!baseDir) {
              return new Map();
    }

    // 动态加载CSV文件
    const csvPath = `${baseDir}/kernel_data/competition_${competitionId}.csv`;
    const contentsManager = app?.serviceManager?.contents;

    if (!contentsManager) {
              return new Map();
    }

            const model = await contentsManager.get(csvPath, { type: 'file', format: 'text', content: true });
    const csvData = csvParse(model.content as string);

    const titleMap = new Map<string, { title: string; creationDate: string; totalLines: number; displayname?: string; url?: string }>();
    csvData.forEach((row: any) => {
      const kernelVersionId = row.KernelVersionId?.toString();
      const title = row.Title;
      const creationDate = row.CreationDate;
      const totalLines = parseFloat(row.TotalLines) || 0;
      const displayname = row.DisplayName || row.displayname; // 支持两种字段名
      const url = row.url; // 添加URL字段
      if (kernelVersionId && title) {
        titleMap.set(kernelVersionId, { title, creationDate, totalLines, displayname, url });
      }
    });

    return titleMap;
  } catch (error) {
            return new Map();
  }
}

// 递归替换对象中的KernelVersionId为Title，并添加CreationDate和TotalLines信息
function replaceKernelVersionIdWithTitle(obj: any, titleMap: Map<string, { title: string; creationDate: string; totalLines: number; displayname?: string; url?: string }>): any {
  if (Array.isArray(obj)) {
    return obj.map(item => replaceKernelVersionIdWithTitle(item, titleMap));
  } else if (obj && typeof obj === 'object') {
    const newObj: any = {};
    for (const [key, value] of Object.entries(obj)) {
      if (key === 'kernelVersionId' && typeof value === 'string') {
        const titleInfo = titleMap.get(value);
        if (titleInfo) {
          newObj.notebook_name = titleInfo.title; // 替换为notebook_name字段
          newObj.kernelVersionId = value; // 保留kernelVersionId用于相似性分组匹配
          newObj.creationDate = titleInfo.creationDate; // 添加创建日期
          newObj.totalLines = titleInfo.totalLines; // 添加总行数
          newObj.displayname = titleInfo.displayname; // 添加displayname
          newObj.url = titleInfo.url; // 添加URL
        } else {
          newObj.kernelVersionId = value; // 保持原值如果找不到对应的title
        }
      } else {
        newObj[key] = replaceKernelVersionIdWithTitle(value, titleMap);
      }
    }
    return newObj;
  }
  return obj;
}



let handleNotebookSelected: ((e: any) => void) | null = null;
let handleSimpleNotebookSelected: ((e: any) => void) | null = null;
let notebookSelectedListenerRegistered = false;
let app: JupyterFrontEnd;
let flowChartWidget: LeftSidebar | null = null;
let detailSidebar: DetailSidebar | null = null;
let result1: any = null;
let mostFreqStage: any = null;
let mostFreqFlow: any = null;
let matrixWidget: MatrixWidget | null = null;

let notebookDetailIds = new Set<string>();
let colorMap: any = null;
let isInitializing = false; // 添加初始化标志

// 添加滚动同步相关的全局变量
let scrollSyncEnabled = false;
let scrollSyncWidgets: Set<string> = new Set();
let scrollSyncHandlers: Map<string, (e: Event) => void> = new Map();
let scrollSyncUpdatePending = false; // 防止频繁更新
let lastScrollSyncState = { hasMultiple: false }; // 记录上次状态
let lockedWidgets: Set<string> = new Set(); // 记录被锁定的widget

function activate(
  appInstance: JupyterFrontEnd,
  palette: ICommandPalette,
  browserFactory: IFileBrowserFactory,
  restorer: ILayoutRestorer | null
) {
  // Extension activated

  const command = 'galaxy:analyze';
  const simpleCommand = 'galaxy:simple-analyze';

  // 将 app 赋值给全局变量
  app = appInstance;

  let lastKnownDetailIds: Set<string> = new Set();


  // ====== 检测主区域是否有分屏布局（包括任何类型的widget） ======
  function hasSplitLayout(): boolean {
    try {
      // 解决方案: 使用 app.shell 的内部 layout 判断是否分屏
      const layout = (app.shell as any).saveLayout();
      const mainArea = layout.mainArea;

      // 添加调试信息
      // 递归检查是否分屏
      function isSplitScreen(area: any): boolean {
        if (!area) return false;

        // 检查是否有 dock.main 结构
        if (area.dock && area.dock.main) {
          return isSplitScreen(area.dock.main);
        }

        if (area.type === 'split-area') {
          // 并行多个子区域（不是单个 tab-area）
          if (area.children && area.children.length > 1) {
            return true;
          }
        }

        // 递归继续判断嵌套结构
        if (area.children) {
          return area.children.some((child: any) => isSplitScreen(child));
        }

        // 如果是 tab-area, 不代表分屏
        if (area.type === 'tab-area') {
          return false;
        }

        return false;
      }

      const split = isSplitScreen(mainArea);

      return split;
    } catch (error) {
              console.error('Error detecting split layout:', error);

      // 降级到之前的DOM检测方法
      const mainWidgets = Array.from(app.shell.widgets('main'));
      const parents = new Set(mainWidgets.map(w => w.parent?.id));

      const mainArea = document.querySelector('.lm-MainArea-widget');
      let hasVisualSplit = false;

      if (mainArea) {
        const splitPanels = mainArea.querySelectorAll('.lm-SplitPanel');
        hasVisualSplit = splitPanels.length > 0;

        const tabBars = mainArea.querySelectorAll('.lm-TabBar');
        const hasMultipleTabBars = tabBars.length > 1;

        const activeTabs = mainArea.querySelectorAll('.lm-TabBar-tab.lm-mod-current');
        const hasMultipleActiveTabs = activeTabs.length > 1;

        const mainAreaChildren = mainArea.children;
        const hasMultipleChildren = mainAreaChildren.length > 1;

        if (hasVisualSplit || hasMultipleTabBars || hasMultipleActiveTabs || hasMultipleChildren || parents.size > 1) {
          return true;
        }
      }

      return false;
    }
  }

  // ====== 检测是否有多个notebook detail widget（排除matrix widget） ======
  function hasMultipleNotebookDetailWidgets(): boolean {
    const mainWidgets = Array.from(app.shell.widgets('main'));
    const notebookDetailWidgets = mainWidgets.filter(w =>
      w.id && w.id.startsWith('notebook-detail-widget-')
    );

    return notebookDetailWidgets.length > 1;
  }

  // ====== 检测是否需要滚动同步（有多个notebook detail widget在分屏中） ======
  function shouldEnableScrollSync(): boolean {
    const hasMultipleNotebookDetails = hasMultipleNotebookDetailWidgets();

    // 如果有多个notebook detail widget，就启用滚动同步
    // 不需要检测整体分屏，因为matrix的存在不影响notebook detail之间的同步
    return hasMultipleNotebookDetails;
  }

  // ====== 设置滚动同步 ======
  function setupScrollSync() {
    // 清除之前的滚动同步
    scrollSyncHandlers.forEach((handler, widgetId) => {
      const widgets = Array.from(app.shell.widgets('main'));
      const widget = widgets.find(w => w.id === widgetId);
      if (widget) {
        const cellList = widget.node.querySelector('#nbd-cell-list-scroll');
        if (cellList) {
          cellList.removeEventListener('scroll', handler);
        }
      }
    });
    scrollSyncHandlers.clear();

    // 检查是否需要启用滚动同步
    const shouldEnable = shouldEnableScrollSync();

    const currentState = { hasMultiple: hasMultipleNotebookDetailWidgets() };
    const stateChanged = currentState.hasMultiple !== lastScrollSyncState.hasMultiple;

    if (stateChanged) {
      lastScrollSyncState = currentState;
    }

    if (shouldEnable) {
      // 启用滚动同步
      scrollSyncEnabled = true;
      scrollSyncWidgets.clear();

      // 收集所有notebook detail widget
      const mainWidgets = Array.from(app.shell.widgets('main'));
      mainWidgets.forEach(widget => {
        if (widget.id && widget.id.startsWith('notebook-detail-widget-')) {
          scrollSyncWidgets.add(widget.id);
        }
      });

      // 为每个widget的滚动容器绑定事件监听器
      scrollSyncWidgets.forEach(widgetId => {
        const widgets = Array.from(app.shell.widgets('main'));
        const widget = widgets.find(w => w.id === widgetId);
        if (widget) {
          const cellList = widget.node.querySelector('#nbd-cell-list-scroll');
          if (cellList) {
            // 移除之前的事件监听器（如果存在）
            const existingHandler = scrollSyncHandlers.get(widgetId);
            if (existingHandler) {
              cellList.removeEventListener('scroll', existingHandler);
            }

            // 创建滚动同步处理器
            const scrollHandler = (e: Event) => {
              if (!scrollSyncEnabled) return;

              const target = e.target as HTMLElement;
              const scrollTop = target.scrollTop;
              const scrollHeight = target.scrollHeight;
              const clientHeight = target.clientHeight;
              const sourceWidgetId = widgetId;

              // 如果源widget被锁定，不进行同步
              if (lockedWidgets.has(sourceWidgetId)) {
                return;
              }

              // 计算滚动百分比
              const maxScrollTop = scrollHeight - clientHeight;
              const scrollPercentage = maxScrollTop > 0 ? scrollTop / maxScrollTop : 0;

              // 只在调试模式下输出滚动日志
              // 临时禁用滚动同步，避免循环触发
              scrollSyncEnabled = false;

              // 同步其他widget的滚动位置（跳过被锁定的widget）
              scrollSyncWidgets.forEach(otherWidgetId => {
                if (otherWidgetId !== sourceWidgetId && !lockedWidgets.has(otherWidgetId)) {
                  const otherWidgets = Array.from(app.shell.widgets('main'));
                  const otherWidget = otherWidgets.find(w => w.id === otherWidgetId);
                  if (otherWidget) {
                    const otherCellList = otherWidget.node.querySelector('#nbd-cell-list-scroll');
                    if (otherCellList) {
                      const otherScrollHeight = otherCellList.scrollHeight;
                      const otherClientHeight = otherCellList.clientHeight;
                      const otherMaxScrollTop = otherScrollHeight - otherClientHeight;

                      // 根据百分比计算目标滚动位置
                      const targetScrollTop = otherMaxScrollTop > 0 ? scrollPercentage * otherMaxScrollTop : 0;

                      // 只有当目标位置与当前位置不同时才设置
                      if (Math.abs(otherCellList.scrollTop - targetScrollTop) > 1) {
                        otherCellList.scrollTop = targetScrollTop;
                      }
                    }
                  }
                }
              });

              // 恢复滚动同步
              scrollSyncEnabled = true;
            };

            // 绑定事件监听器
            cellList.addEventListener('scroll', scrollHandler);
            scrollSyncHandlers.set(widgetId, scrollHandler);

          } else {
            console.warn('[Scroll Sync] No cell list found for widget:', widgetId);
          }
        } else {
          console.warn('[Scroll Sync] Widget not found:', widgetId);
        }
      });

    } else {
      // 禁用滚动同步
      scrollSyncEnabled = false;

      // 移除所有widget的滚动事件监听器
      const mainWidgets = Array.from(app.shell.widgets('main'));
      mainWidgets.forEach(widget => {
        if (widget.id && widget.id.startsWith('notebook-detail-widget-')) {
          const cellList = widget.node.querySelector('#nbd-cell-list-scroll');
          if (cellList) {
            const handler = scrollSyncHandlers.get(widget.id);
            if (handler) {
              cellList.removeEventListener('scroll', handler);
            }
          }
        }
      });

      scrollSyncWidgets.clear();
      scrollSyncHandlers.clear();
    }
  }

  // ====== 更新滚动同步状态 ======
  function updateScrollSync() {
    if (scrollSyncUpdatePending) return;
    scrollSyncUpdatePending = true;

    // 使用 requestAnimationFrame 确保在下一帧执行，避免频繁调用
    requestAnimationFrame(() => {
      setupScrollSync();
      scrollSyncUpdatePending = false;
    });
  }

  // ====== handleTabSwitch 放回 activate 内部，直接访问最新 sidebar 变量 ======
  let previousTabId: string | null = null;

  function handleTabSwitch(widget: any) {
    // 检查simple notebook detail widget
    if (widget && widget.id && widget.id.startsWith('simple-notebook-detail-widget-')) {
      // 更新SimpleInfoSidebar
      const rightWidgets = Array.from(app.shell.widgets('right'));
      const simpleInfoSidebar = rightWidgets.find(w => w.id === 'simple-info-sidebar');
      if (simpleInfoSidebar && widget.notebook) {
        (simpleInfoSidebar as any).setNotebookDetail(widget.notebook);
      }
      return;
    }
    
    // 检查simple notebook list widget
    if (widget && widget.id === 'simple-notebook-list-widget') {
      // 切换回list时，清除notebook详情，恢复总体统计
      const rightWidgets = Array.from(app.shell.widgets('right'));
      const simpleInfoSidebar = rightWidgets.find(w => w.id === 'simple-info-sidebar');
      if (simpleInfoSidebar) {
        (simpleInfoSidebar as any).clearNotebook();
      }
      return;
    }
    
    // 新增：如果 widget 为空或不是 galaxy 相关 tab，检查是否需要关闭 sidebar
    if (!widget || !(widget.id && (widget.id === 'matrix-widget' || widget.id.startsWith('notebook-detail-widget-')))) {
      // 只有在没有galaxy分析数据时才关闭sidebar
      if (!result1 || result1.length === 0) {
        closeSidebarsIfNoMainWidgets(app);
      }
      return;
    }
    const tabId = widget.id || '';

    // Track tab switch if we have a previous tab
    if (previousTabId && previousTabId !== tabId) {
      let tabType: 'matrix' | 'notebook_detail' | 'other' = 'other';
      let notebookName: string | undefined;
      let competitionId: string | undefined;

      if (tabId === 'matrix-widget') {
        tabType = 'matrix';
      } else if (tabId.startsWith('notebook-detail-widget-')) {
        tabType = 'notebook_detail';
        if (widget.notebook) {
          notebookName = widget.notebook.notebook_name;
          competitionId = widget.notebook.competitionId;
        }
      }

      analytics.trackTabSwitch({
        fromTab: previousTabId,
        toTab: tabId,
        tabType: tabType,
        notebookName: notebookName,
        competitionId: competitionId
      });
    }

    // Update previous tab tracking
    previousTabId = tabId;

    // 检查是否有分屏布局
    if (hasSplitLayout()) {
      // 收缩左右sidebar而不是关闭
      if (typeof (app.shell as any).collapseLeft === 'function') {
        (app.shell as any).collapseLeft();
      }
      if (typeof (app.shell as any).collapseRight === 'function') {
        (app.shell as any).collapseRight();
      }
      // 在分屏布局下也需要更新滚动同步
      setTimeout(() => updateScrollSync(), 100);
      return;
    }

    if (tabId.startsWith('notebook-detail-widget-') && widget.notebook) {
      // notebook detail tab
      // 确保notebook detail widget可见并激活
      ensureWidgetVisibleAndActive(widget);

      const nb = widget.notebook;
      // 确保 colorMap 包含该 notebook 中的所有 stage
      const singleNotebookStages = new Set<string>();
      nb.cells.forEach((cell: any) => {
        if ((cell.cellType + '').toLowerCase() === 'code') {
          const stage = String(cell["1st-level label"] ?? "None");
          singleNotebookStages.add(stage);
        }
      });
      initColorMap(singleNotebookStages);
      // 保证左侧只保留 flowChartWidget
      const leftWidgets = Array.from(app.shell.widgets('left'));
      for (const w of leftWidgets) {
        if (w !== flowChartWidget && w.id === 'flow-chart-widget') w.close();
      }
      flowChartWidget?.setData([nb], colorMapModule);
      if (flowChartWidget) {
        app.shell.add(flowChartWidget, 'left');
        app.shell.activateById(flowChartWidget.id);
      }
      detailSidebar?.setNotebookDetail(nb, true); // 跳过事件派发，避免循环
      if (detailSidebar) {
        app.shell.add(detailSidebar, 'right');
        app.shell.activateById(detailSidebar.id);
      }
      return;
    }
    if (tabId === 'matrix-widget') {
      // overview tab
      // 确保matrix widget可见并激活
      ensureWidgetVisibleAndActive(matrixWidget);

      // 确保 colorMap 包含所有 stage
      const allStages = new Set<string>();
      result1.forEach((nb: any) => {
        nb.cells.forEach((cell: any) => {
          if ((cell.cellType + '').toLowerCase() === 'code') {
            const stage = String(cell["1st-level label"] ?? "None");
            allStages.add(stage);
          }
        });
      });
      initColorMap(allStages);
      // 保证左侧只保留 flowChartWidget
      const leftWidgets = Array.from(app.shell.widgets('left'));
      for (const w of leftWidgets) {
        if (w !== flowChartWidget && w.id === 'flow-chart-widget') w.close();
      }
      flowChartWidget?.setData(result1, colorMapModule);
      if (flowChartWidget) {
        app.shell.add(flowChartWidget, 'left');
        app.shell.activateById(flowChartWidget.id);
      }
      if (flowChartWidget && matrixWidget && result1 && detailSidebar) {
        const { mostFreqStage, mostFreqFlow } = flowChartWidget.getMostFrequentStageAndFlow();


        // 检查detailSidebar是否已经在右侧
        const rightWidgets = Array.from(app.shell.widgets('right'));
        const isAlreadyInRight = rightWidgets.includes(detailSidebar);

        detailSidebar.setSummary(result1, mostFreqStage, mostFreqFlow, matrixWidget?.getNotebookOrder?.());

        if (!isAlreadyInRight) {
          app.shell.add(detailSidebar, 'right');
        }
        app.shell.activateById(detailSidebar.id);
      }
      return;
    }
    // 其它 tab 不更新 sidebar，但也不关闭sidebar
  }

  // ====== closeSidebarsIfNoMainWidgets 也放到 activate 内部，能访问 handleTabSwitch ======
  function closeSidebarsIfNoMainWidgets(app: JupyterFrontEnd) {
    // 在初始化过程中不关闭sidebar
    if (isInitializing) {
      return;
    }

    const mainWidgets = Array.from(app.shell.widgets('main'));
    const hasMatrix = mainWidgets.some(w => w.id === 'matrix-widget');
    const hasDetail = mainWidgets.some(w => w.id && w.id.startsWith('notebook-detail-widget-'));
    const hasSimpleList = mainWidgets.some(w => w.id === 'simple-notebook-list-widget');

    // 检查是否有分屏布局
    if (hasSplitLayout()) {
      // 收缩左右sidebar而不是关闭
      if (typeof (app.shell as any).collapseLeft === 'function') {
        (app.shell as any).collapseLeft();
      }
      if (typeof (app.shell as any).collapseRight === 'function') {
        (app.shell as any).collapseRight();
      }
      return;
    }

    // 当没有galaxy相关tab时关闭sidebar
    if (!hasMatrix && !hasDetail && !hasSimpleList) {
      // 关闭sidebar，不管是否有分析数据
      // 关闭左侧 flowchart
      const oldLeft = app.shell.widgets('left');
      for (const w of oldLeft) {
        if (w.id === 'flow-chart-widget') {
          w.close();
        }
      }
      // 关闭右侧 detail sidebar 和 simple info sidebar
      const oldRight = app.shell.widgets('right');
      for (const w of oldRight) {
        if (w.id === 'galaxy-detail-sidebar' || w.id === 'simple-info-sidebar') {
          w.close();
        }
      }
    }
  }

  // 辅助函数：确保widget可见并激活
  function ensureWidgetVisibleAndActive(widget: any) {
    if (!widget) return false;

    // 如果widget不可见，尝试激活它
    if (!widget.isVisible) {
      app.shell.activateById(widget.id);
    }

    return widget.isVisible;
  }

  // 恢复：获取主区域第一个 galaxy 相关 widget（优先 notebook-detail-widget，其次 matrix-widget，最后 simple-notebook-list-widget）
  function getActiveGalaxyWidget() {
    const mainWidgets = Array.from(app.shell.widgets('main'));

    // 首先检查可见的galaxy widget
    const visibleGalaxyWidgets = mainWidgets.filter(w =>
      w.isVisible && (
        (w.id && w.id.startsWith('notebook-detail-widget-')) ||
        (w.id && w.id === 'matrix-widget') ||
        (w.id && w.id === 'simple-notebook-list-widget')
      )
    );

    // 如果有可见的galaxy widget，优先使用第一个
    if (visibleGalaxyWidgets.length > 0) {
      return visibleGalaxyWidgets[0];
    }

    // 如果没有可见的，按原来的逻辑查找
    let widget = mainWidgets.find(w => w.id && w.id.startsWith('notebook-detail-widget-'));
    if (!widget) {
      widget = mainWidgets.find(w => w.id && w.id === 'matrix-widget');
    }
    if (!widget) {
      widget = mainWidgets.find(w => w.id && w.id === 'simple-notebook-list-widget');
    }

    return widget || null;
  }

  app.commands.addCommand(command, {
    label: 'Condition B',
    execute: async () => {
      isInitializing = true; // 设置初始化标志

      const fileBrowserWidget = browserFactory.tracker.currentWidget;
      if (!fileBrowserWidget) {
        console.warn('No active file browser');
        return;
      }

      const selectedItems = Array.from(fileBrowserWidget.selectedItems());

      try {
        // 初始化变量
        let similarityGroups: any[] = [];
        let voteData: any[] = [];
        let summaryData: any = null;

        // 关闭之前的所有galaxy相关窗口和sidebar
        const oldLeft = app.shell.widgets('left');
        for (const w of oldLeft) {
          if (w.id === 'flow-chart-widget' || w.id === 'simple-notebook-list-widget') w.close();
        }
        const oldMain = app.shell.widgets('main');
        for (const w of oldMain) {
          if (w.id === 'matrix-widget' || 
              (w.id && w.id.startsWith('notebook-detail-widget-')) ||
              w.id === 'simple-notebook-list-widget' ||
              (w.id && w.id.startsWith('simple-notebook-detail-widget-')) ||
              (w.id && w.id.includes('simple-notebook'))) {
            // Track notebook closing before closing
            if (w.id && w.id.startsWith('notebook-detail-widget-')) {
              const notebookData = (w as any).notebook;
              if (notebookData) {
                analytics.trackNotebookClosed(
                  notebookData.kernelVersionId || `nb_${notebookData.index || Date.now()}`,
                  {
                    tabTitle: w.title?.label,
                    tabId: w.id
                  }
                );
              }
            }
            w.close();
          }
        }
        const oldRight = app.shell.widgets('right');
        for (const w of oldRight) {
          if (w.id === 'galaxy-detail-sidebar' || w.id === 'simple-info-sidebar') w.close();
        }
        
        // 额外的清理：确保所有包含 'simple' 或 'galaxy' 的widget都被关闭
        const allMainWidgets = app.shell.widgets('main');
        for (const w of allMainWidgets) {
          if (w.id && (w.id.includes('simple') || w.id.includes('galaxy'))) {
            console.log('Closing additional widget:', w.id);
            w.close();
          }
        }

        // 清理 notebook detail IDs 记录
        notebookDetailIds.clear();
        lastKnownDetailIds.clear();

        // 重置全局变量
        flowChartWidget = null;
        detailSidebar = null;
        matrixWidget = null;
        result1 = null;
        mostFreqStage = null;
        mostFreqFlow = null;
        colorMap = null;

        // 清除滚动同步状态
        scrollSyncEnabled = false;
        scrollSyncWidgets.clear();
        scrollSyncHandlers.clear();
        lockedWidgets.clear();

        // 移除所有galaxy相关的事件监听器
        if (handleNotebookSelected) {
          window.removeEventListener('galaxy-notebook-selected', handleNotebookSelected);
        }
        if (handleSimpleNotebookSelected) {
          window.removeEventListener('galaxy-simple-notebook-selected', handleSimpleNotebookSelected);
        }

        // 重置事件监听器注册标志
        notebookSelectedListenerRegistered = false;
        handleNotebookSelected = null;
        handleSimpleNotebookSelected = null;
        // 清除防重复状态
        (window as any)._lastProcessedNotebookEvent = null;

        // 检查是否选中了JSON文件
        if (
          selectedItems.length === 1 &&
          selectedItems[0].type === 'file' &&
          selectedItems[0].path.endsWith('.json')
        ) {
          // 直接用 Contents API 读取 JSON 文件内容
          const contentsManager = app.serviceManager.contents;
          const model = await contentsManager.get(selectedItems[0].path, { type: 'file', format: 'text', content: true });
          result1 = JSON.parse(model.content as string);


          // 提取competition ID和基础目录
          const competitionId = extractCompetitionId(selectedItems[0].path);

          // Track analysis started
          analytics.trackAnalysisStarted({
            competitionId: competitionId || undefined,
            totalNotebooks: result1.length,
            jsonFilePath: selectedItems[0].path
          });
          const baseDir = extractBaseDir(selectedItems[0].path);

          if (competitionId && baseDir) {
            try {
              const titleMap = await createKernelTitleMap(competitionId, baseDir);
              result1 = replaceKernelVersionIdWithTitle(result1, titleMap);
            } catch (e) {
              // Kernel data not available
            }

            // 加载并合并TOC数据（如果存在）
            if (baseDir) {
              try {
                const tocData = await loadTocData(competitionId, baseDir);
                result1 = mergeTocData(result1, tocData);
              } catch (e) {
                // TOC data not available
              }
            }

            // 加载Summary数据（如果存在）
            if (baseDir) {
              try {
                summaryData = await loadSummaryData(competitionId, baseDir);
              } catch (e) {
                // Summary data not available
              }
            }

            // 读取对应的 CSV 文件（如果存在）
            try {
              const csvPath = `${baseDir}/cluster_data/${competitionId}_sorted.csv`;
              const csvModel = await contentsManager.get(csvPath, { type: 'file', format: 'text', content: true });
              similarityGroups = csvParse(csvModel.content as string);
            } catch (e) {
              similarityGroups = [];
            }

            // 读取投票数据（如果存在）
            try {
              const votePath = `${baseDir}/cluster_data/${competitionId}_sorted.csv`;
              const voteModel = await contentsManager.get(votePath, { type: 'file', format: 'text', content: true });
              voteData = csvParse(voteModel.content as string);
            } catch (e) {
              voteData = [];
            }
          }
        } else {
          // 只支持JSON文件分析
          console.warn('Please select a single JSON file for analysis');
          return;
        }

        // 统一颜色映射
        const allStages = new Set<string>();
        result1.forEach((nb: any) => {
          nb.cells.forEach((cell: any) => {
            if ((cell.cellType + '').toLowerCase() === 'code') {
              const stage = String(cell["1st-level label"] ?? "None");
              allStages.add(stage);
            }
          });
        });
        initColorMap(allStages);
        colorMap = colorMapModule; // 确保 colorMap 全局可用


        flowChartWidget = new LeftSidebar(result1, colorMap, true); // Overview mode
        app.shell.add(flowChartWidget, 'left');

        if (typeof (app.shell as any).expandLeftArea === 'function') {
          (app.shell as any).expandLeftArea();
        }

        app.shell.activateById(flowChartWidget.id);
        // 保存原始 sidebar 和数据，便于 notebook 详情切换回来
        // let originalLeftSidebar = flowChartWidget;

        // 添加 MatrixWidget 到主区域
        const colorScale = (label: string) => colorMapModule.get(label) || '#fff';

        // 创建kernelTitleMap用于MatrixWidget
        let kernelTitleMap = new Map<string, { title: string; creationDate: string; totalLines: number; displayname?: string; url?: string }>();

        // 重新获取competitionId和基础目录
        let competitionIdForMatrix: string | null = null;
        let baseDirForMatrix: string | null = null;
        if (selectedItems.length === 1 && selectedItems[0].type === 'file' && selectedItems[0].path.endsWith('.json')) {
          competitionIdForMatrix = extractCompetitionId(selectedItems[0].path);
          baseDirForMatrix = extractBaseDir(selectedItems[0].path);
        }

        if (competitionIdForMatrix && baseDirForMatrix) {
          kernelTitleMap = await createKernelTitleMap(competitionIdForMatrix, baseDirForMatrix);
        }

        // 获取competition信息
        let competitionInfo: { id: string; name: string; url: string; description?: string; category?: string; evaluation?: string; startDate?: string; endDate?: string } | undefined = undefined;
        if (competitionIdForMatrix) {
          competitionInfo = await getCompetitionInfo(competitionIdForMatrix, baseDirForMatrix || undefined) || undefined;
        }

        matrixWidget = new MatrixWidget(result1, colorScale, similarityGroups, kernelTitleMap, voteData, summaryData, competitionInfo);
        app.shell.add(matrixWidget, 'main');
        app.shell.activateById(matrixWidget.id);
        matrixWidget.disposed.connect(() => {
          closeSidebarsIfNoMainWidgets(app);
        });
        const notebookOrder = matrixWidget.getNotebookOrder();

        const detailSidebarInstance = new DetailSidebar(colorMapModule, notebookOrder, undefined, similarityGroups, voteData, competitionInfo);
        detailSidebar = detailSidebarInstance;
        const { mostFreqStage: mfs, mostFreqFlow: mff } = flowChartWidget.getMostFrequentStageAndFlow();
        mostFreqStage = mfs;
        mostFreqFlow = mff;
        detailSidebar.setSummary(result1, mostFreqStage, mostFreqFlow, matrixWidget.getNotebookOrder());
        app.shell.add(detailSidebar, 'right');
        if (typeof (app.shell as any).expandRightArea === 'function') {
          (app.shell as any).expandRightArea();
        }
        app.shell.activateById(detailSidebar.id);

        // 确保左侧sidebar保持可见
        if (flowChartWidget && !flowChartWidget.isDisposed) {
          app.shell.activateById(flowChartWidget.id);
        }

        // 监听 notebook 排序变化，实时同步 sidebar
        window.addEventListener('galaxy-notebook-order-changed', (e: any) => {
          detailSidebar?.setSummary(result1, mostFreqStage, mostFreqFlow, e.detail?.notebookOrder);
        });

        // 统一管理 flowchart/matrix/detail 的筛选联动（按tab隔离）
        let currentSelection: any = null;
        window.addEventListener('galaxy-stage-selected', (e: any) => {
          const { stage, tabId } = e.detail;
          currentSelection = { type: 'stage', stage, tabId };
          // 移除对matrix的filter调用，让matrix不再跟随notebook detail tab的选择
          // matrixWidget?.setFilter(currentSelection);

          // 如果有cluster被选中，不要改变右侧sidebar的状态
          const hasSelectedCluster = matrixWidget && (matrixWidget as any).selectedClusterId && (matrixWidget as any).sortState === 3;
          if (!hasSelectedCluster) {
            detailSidebar?.setFilter(currentSelection, true); // 跳过事件派发，避免循环
          }

          // Track flowchart interaction
          analytics.trackFlowChartInteraction('stage_selected', {
            stage: stage,
            tabId: tabId,
            flowchartContext: 'overview', // These events come from the main overview
            interaction_context: 'stage_filter'
          });
        });
        window.addEventListener('galaxy-flow-selected', (e: any) => {
          const { from, to, tabId } = e.detail;
          currentSelection = { type: 'flow', from, to, tabId };
          // 移除对matrix的filter调用，让matrix不再跟随notebook detail tab的选择
          // matrixWidget?.setFilter(currentSelection);

          // 如果有cluster被选中，不要改变右侧sidebar的状态
          const hasSelectedCluster = matrixWidget && (matrixWidget as any).selectedClusterId && (matrixWidget as any).sortState === 3;
          if (!hasSelectedCluster) {
            detailSidebar?.setFilter(currentSelection, true); // 跳过事件派发，避免循环
          }

          // Track flowchart interaction
          analytics.trackFlowChartInteraction('flow_selected', {
            from: from,
            to: to,
            tabId: tabId,
            flowchartContext: 'overview', // These events come from the main overview
            interaction_context: 'flow_filter'
          });
        });
        window.addEventListener('galaxy-selection-cleared', (e: any) => {
          // const tabId = e.detail?.tabId;
          // Only track analytics if there was actually a selection to clear
          const hadSelection = currentSelection !== null;
          currentSelection = null;
          // 移除对matrix的filter调用，让matrix不再跟随notebook detail tab的选择
          // matrixWidget?.setFilter(null);
          detailSidebar?.setFilter(null, true); // 跳过事件派发，避免循环
          // Track flowchart interaction only when there was a selection to clear
          if (hadSelection) {
            analytics.trackFlowChartInteraction('selection_cleared', {
              tabId: e.detail?.tabId,
              flowchartContext: 'overview', // These events come from the main overview
              interaction_context: 'clear_filter'
            });
          }
        });

        // 监听TOC项目点击事件
        window.addEventListener('galaxy-toc-item-clicked', (e: any) => {
          const { cellId } = e.detail;

          // 解析cellId，格式为 "kernelVersionId_cellIndex"
          const [kernelVersionId, cellIndexStr] = cellId.split('_');
          const cellIndex = parseInt(cellIndexStr);

          // 找到对应的notebook
          const notebook = result1.find((nb: any) => nb.kernelVersionId === kernelVersionId);
          if (notebook) {
            // 使用notebook在result1数组中的索引，而不是globalIndex
            const notebookIndex = result1.indexOf(notebook);

            // 跳转到对应的cell
            window.dispatchEvent(new CustomEvent('galaxy-notebook-detail-jump', {
              detail: {
                notebookIndex: notebookIndex,
                cellIndex: cellIndex,
                kernelVersionId: kernelVersionId
              }
            }));
          } else {
            // Notebook not found
          }
        });

        // 定义 notebook 详情切换处理函数（只定义一次）
        if (!handleNotebookSelected) {
          handleNotebookSelected = function (e: any) {
            // 防止重复处理相同的事件（在短时间内）
            const notebookId = e.detail.notebook.kernelVersionId || e.detail.notebook.index;
            const now = Date.now();
            const lastProcessed = (window as any)._lastProcessedNotebookEvent;
            
            if (lastProcessed && 
                lastProcessed.notebookId === notebookId && 
                now - lastProcessed.timestamp < 1000) { // 1秒内的重复事件
              return; // 跳过重复事件
            }
            
            (window as any)._lastProcessedNotebookEvent = {
              notebookId: notebookId,
              timestamp: now
            };
            
            // 新建并显示 notebook 详情，深拷贝 notebook 数据
            const nb = JSON.parse(JSON.stringify(e.detail.notebook));
            const nbDetailWidget = new NotebookDetailWidget(nb);
            nbDetailWidget.id = `notebook-detail-widget-${nb.kernelVersionId || nb.index || Date.now()}`;

            // Record opening time for session tracking
            (nbDetailWidget as any)._openTime = Date.now();

            app.shell.add(nbDetailWidget, 'main');
            app.shell.activateById(nbDetailWidget.id);
            notebookDetailIds.add(nbDetailWidget.id);

            // Track notebook opened
            analytics.trackNotebookOpened({
              kernelVersionId: nb.kernelVersionId || `nb_${nb.index || Date.now()}`,
              notebookName: nb.notebook_name,
              competitionId: competitionIdForMatrix || undefined,
              totalCells: nb.cells ? nb.cells.length : 0,
              codeCells: nb.cells ? nb.cells.filter((cell: any) => (cell.cellType + '').toLowerCase() === 'code').length : 0,
              tabTitle: nbDetailWidget.title.label, // Use actual tab title (e.g., "Notebook 1", "Notebook 2")
              tabId: nbDetailWidget.id
            });
            nbDetailWidget.disposed.connect(() => {
              // Track notebook closed
              analytics.trackNotebookClosed(
                nb.kernelVersionId || `nb_${nb.index || Date.now()}`,
                {
                  tabTitle: nbDetailWidget.title.label, // Use actual tab title (e.g., "Notebook 1", "Notebook 2")
                  tabId: nbDetailWidget.id
                }
              );

              // Remove from tracking set
              notebookDetailIds.delete(nbDetailWidget.id);

              // Check for split screen deactivation
              const remainingNotebooks = notebookDetailIds.size;
              if (remainingNotebooks === 1) {
                // Split screen just ended (went from 2+ to 1 notebook)
                analytics.trackSplitScreenDeactivated({
                  previousNotebookCount: remainingNotebooks + 1,
                  remainingNotebooks: remainingNotebooks,
                  sessionDuration: Date.now() - (nbDetailWidget as any)._openTime || 0,
                  deactivationReason: 'notebook_closed'
                });
              }



              // 清理滚动同步状态
              updateScrollSync();
            });

            // 延迟更新滚动同步状态，避免频繁调用
            setTimeout(() => updateScrollSync(), 100);



            // 检查是否有分屏布局
            if (hasSplitLayout()) {
              // 获取当前打开的notebook列表用于分屏事件追踪
              const openNotebooks = Array.from(notebookDetailIds).map(id => {
                const widget = Array.from(app.shell.widgets('main')).find(w => w.id === id) as any;
                return { notebookId: widget?.title?.label, notebook: widget?.notebook };
              }).filter(item => item.notebookId && item.notebook);

              // Track split screen activation
              analytics.trackSplitScreenActivated({
                totalNotebooks: openNotebooks.length + 1, // +1 for the newly opened notebook
                notebookIds: [...openNotebooks.map(item => item.notebookId), nbDetailWidget.title.label].filter(Boolean),
                notebookNames: [...openNotebooks.map(item => item.notebook.notebook_name), nb.notebook_name].filter(Boolean),
                competitionId: competitionIdForMatrix || undefined,
                triggerAction: 'new_notebook_opened'
              });

              // 收缩左右sidebar而不是关闭
              if (typeof (app.shell as any).collapseLeft === 'function') {
                (app.shell as any).collapseLeft();
              }
              if (typeof (app.shell as any).collapseRight === 'function') {
                (app.shell as any).collapseRight();
              }
              // 在分屏布局下也需要更新滚动同步
              setTimeout(() => updateScrollSync(), 100);
              return; // 不创建sidebar，直接返回
            }

            // 新建只显示该 notebook 的 flowchart
            // 确保 colorMap 包含该 notebook 中的所有 stage
            const singleNotebookStages = new Set<string>();
            nb.cells.forEach((cell: any) => {
              if ((cell.cellType + '').toLowerCase() === 'code') {
                const stage = String(cell["1st-level label"] ?? "None");
                singleNotebookStages.add(stage);
              }
            });
            // 重新初始化 colorMap 以包含该 notebook 的所有 stage
            initColorMap(singleNotebookStages);
            const singleLeftSidebar = new LeftSidebar([nb], colorMapModule, false); // Notebook detail mode
            app.shell.add(singleLeftSidebar, 'left');
            setTimeout(() => {
              if (typeof (app.shell as any).expandLeftArea === 'function') {
                (app.shell as any).expandLeftArea();
              }
              app.shell.activateById(singleLeftSidebar.id);
            }, 0);

            // 右侧 sidebar 只显示该 notebook 信息，清除之前的filter状态
            detailSidebar?.setFilter(null);
            detailSidebar?.setNotebookDetail(nb, true); // 跳过事件派发，避免循环

            // 只关闭左侧 flow-chart-widget（overview），不关闭 matrix-widget
            const oldLeft = app.shell.widgets('left');
            for (const w of oldLeft) {
              if (w.id === 'flow-chart-widget' && w !== singleLeftSidebar) w.close();
            }

            // 新增：如果有 jumpCellIndex，自动 jump 到 cell
            if (e.detail.jumpCellIndex !== undefined) {
              setTimeout(() => {
                window.dispatchEvent(new CustomEvent('galaxy-notebook-detail-jump', {
                  detail: {
                    notebookIndex: nb.index,
                    cellIndex: e.detail.jumpCellIndex,
                    kernelVersionId: nb.kernelVersionId
                  }
                }));
              }, 0);
            }

            // 返回事件
            const handleBack = () => {
              // 关闭 notebook 详情
              const mainWidgets = app.shell.widgets('main');
              for (const w of mainWidgets) {
                if (w.id === 'notebook-detail-widget') {
                  // Track notebook closing before closing
                  const notebookData = (w as any).notebook;
                  if (notebookData) {
                    analytics.trackNotebookClosed(
                      notebookData.kernelVersionId || `nb_${notebookData.index || Date.now()}`,
                      {
                        tabTitle: w.title?.label,
                        tabId: w.id
                      }
                    );
                  }
                  w.close();
                }
              }
              // 关闭当前 flow-chart-widget
              const leftWidgets = app.shell.widgets('left');
              for (const w of leftWidgets) {
                if (w.id === 'flow-chart-widget') w.close();
              }
              // 恢复原始 LeftSidebar，并确保 colorMap 包含所有 stage
              const allStages = new Set<string>();
              result1.forEach((nb: any) => {
                nb.cells.forEach((cell: any) => {
                  if ((cell.cellType + '').toLowerCase() === 'code') {
                    const stage = String(cell["1st-level label"] ?? "None");
                    allStages.add(stage);
                  }
                });
              });
              initColorMap(allStages);
              flowChartWidget?.setData(result1, colorMapModule);
              app.shell.add(flowChartWidget!, 'left');
              app.shell.activateById(flowChartWidget!.id);
              // matrix-widget 保持不变
              // 恢复 summary 视图，清除filter状态
              detailSidebar?.setFilter(null);
              detailSidebar?.setSummary(result1, mostFreqStage, mostFreqFlow, matrixWidget?.getNotebookOrder?.());
              window.removeEventListener('galaxy-notebook-detail-back', handleBack);
            };
            window.addEventListener('galaxy-notebook-detail-back', handleBack);
          };
          // 只注册一次 notebook 详情切换监听器
          if (!notebookSelectedListenerRegistered && handleNotebookSelected) {
            window.addEventListener('galaxy-notebook-selected', handleNotebookSelected);
            notebookSelectedListenerRegistered = true;
          }


        }
      } catch (err) {

        console.error('Failed to analyze notebooks:', err);
      } finally {
        isInitializing = false; // 清除初始化标志
      }
    }
  });

  // 添加简化分析命令
  app.commands.addCommand(simpleCommand, {
    label: 'Condition A',
    execute: async () => {
      isInitializing = true; // 设置初始化标志

      const fileBrowserWidget = browserFactory.tracker.currentWidget;
      if (!fileBrowserWidget) {
        console.warn('No active file browser');
        return;
      }

      const selectedItems = Array.from(fileBrowserWidget.selectedItems());

      try {
        // 关闭之前的所有galaxy相关窗口和sidebar
        const oldLeft = app.shell.widgets('left');
        for (const w of oldLeft) {
          if (w.id === 'flow-chart-widget' || w.id === 'simple-notebook-list-widget') w.close();
        }
        const oldMain = app.shell.widgets('main');
        for (const w of oldMain) {
          if (w.id === 'matrix-widget' || 
              (w.id && w.id.startsWith('notebook-detail-widget-')) ||
              w.id === 'simple-notebook-list-widget' ||
              (w.id && w.id.startsWith('simple-notebook-detail-widget-')) ||
              (w.id && w.id.includes('simple-notebook'))) {
            // Track notebook closing before closing
            if (w.id && w.id.startsWith('notebook-detail-widget-')) {
              const notebookData = (w as any).notebook;
              if (notebookData) {
                analytics.trackNotebookClosed(
                  notebookData.kernelVersionId || `nb_${notebookData.index || Date.now()}`,
                  {
                    tabTitle: w.title?.label,
                    tabId: w.id
                  }
                );
              }
            }
            w.close();
          }
        }
        const oldRight = app.shell.widgets('right');
        for (const w of oldRight) {
          if (w.id === 'simple-info-sidebar' || w.id === 'galaxy-detail-sidebar') w.close();
        }
        
        // 额外的清理：确保所有包含 'simple' 或 'galaxy' 的widget都被关闭
        const allMainWidgets = app.shell.widgets('main');
        for (const w of allMainWidgets) {
          if (w.id && (w.id.includes('simple') || w.id.includes('galaxy') || w.id.includes('matrix'))) {
            console.log('Closing additional widget:', w.id);
            w.close();
          }
        }
        
        // 清理所有侧边栏中的相关widget
        const allLeftWidgets = app.shell.widgets('left');
        for (const w of allLeftWidgets) {
          if (w.id && (w.id.includes('simple') || w.id.includes('galaxy') || w.id.includes('flow'))) {
            console.log('Closing additional left widget:', w.id);
            w.close();
          }
        }
        
        const allRightWidgets = app.shell.widgets('right');
        for (const w of allRightWidgets) {
          if (w.id && (w.id.includes('simple') || w.id.includes('galaxy'))) {
            console.log('Closing additional right widget:', w.id);
            w.close();
          }
        }

        // 清理 notebook detail IDs 记录
        notebookDetailIds.clear();
        lastKnownDetailIds.clear();

        // 重置全局变量
        flowChartWidget = null;
        detailSidebar = null;
        matrixWidget = null;
        result1 = null;
        mostFreqStage = null;
        mostFreqFlow = null;
        colorMap = null;

        // 清除滚动同步状态
        scrollSyncEnabled = false;
        scrollSyncWidgets.clear();
        scrollSyncHandlers.clear();
        lockedWidgets.clear();

        // 移除所有galaxy相关的事件监听器
        if (handleNotebookSelected) {
          window.removeEventListener('galaxy-notebook-selected', handleNotebookSelected);
        }
        if (handleSimpleNotebookSelected) {
          window.removeEventListener('galaxy-simple-notebook-selected', handleSimpleNotebookSelected);
        }

        // 重置事件监听器注册标志
        notebookSelectedListenerRegistered = false;
        handleNotebookSelected = null;
        handleSimpleNotebookSelected = null;
        // 清除防重复状态
        (window as any)._lastProcessedNotebookEvent = null;

        // 检查是否选中了JSON文件
        if (
          selectedItems.length === 1 &&
          selectedItems[0].type === 'file' &&
          selectedItems[0].path.endsWith('.json')
        ) {
          // 直接用 Contents API 读取 JSON 文件内容
          const contentsManager = app.serviceManager.contents;
          const model = await contentsManager.get(selectedItems[0].path, { type: 'file', format: 'text', content: true });
          result1 = JSON.parse(model.content as string);

          // 提取competition ID和基础目录
          const competitionId = extractCompetitionId(selectedItems[0].path);
          const baseDir = extractBaseDir(selectedItems[0].path);

          // Track analysis started
          analytics.trackAnalysisStarted({
            competitionId: competitionId || undefined,
            totalNotebooks: result1.length,
            jsonFilePath: selectedItems[0].path
          });

          // 获取competition信息
          let competitionInfo: { id: string; name: string; url: string; description?: string; category?: string; evaluation?: string; startDate?: string; endDate?: string } | undefined = undefined;
          if (competitionId) {
            competitionInfo = await getCompetitionInfo(competitionId, baseDir || undefined) || undefined;
          }

          // 创建kernelTitleMap
          let kernelTitleMap = new Map<string, { title: string; creationDate: string; totalLines: number; displayname?: string; url?: string }>();
          let voteData: any[] = [];
          
          if (competitionId && baseDir) {
            try {
              kernelTitleMap = await createKernelTitleMap(competitionId, baseDir);
              result1 = replaceKernelVersionIdWithTitle(result1, kernelTitleMap);
            } catch (e) {
              // Kernel data not available
            }

            // 加载TOC数据并合并到notebook数据中
            try {
              const tocData = await loadTocData(competitionId, baseDir);
              result1 = mergeTocData(result1, tocData);
            } catch (e) {
              // TOC data not available
            }

            // 读取投票数据（如果存在）
            try {
              const votePath = `${baseDir}/cluster_data/${competitionId}_sorted.csv`;
              const voteModel = await contentsManager.get(votePath, { type: 'file', format: 'text', content: true });
              voteData = csvParse(voteModel.content as string);
            } catch (e) {
              voteData = [];
            }
          }

          // 创建简化的notebook列表widget
          const simpleListWidget = new SimpleNotebookListWidget(result1, kernelTitleMap, competitionInfo, voteData);
          app.shell.add(simpleListWidget, 'main');
          app.shell.activateById(simpleListWidget.id);

          // 创建简化的信息侧边栏
          const simpleInfoSidebar = new SimpleInfoSidebar(competitionInfo);
          app.shell.add(simpleInfoSidebar, 'right');
          if (typeof (app.shell as any).expandRightArea === 'function') {
            (app.shell as any).expandRightArea();
          }
          app.shell.activateById(simpleInfoSidebar.id);

          // 注册 simple notebook detail 事件监听器（合并处理）
          handleSimpleNotebookSelected = (e: any) => {
            // 新建并显示 simple notebook 详情，深拷贝 notebook 数据
            const nb = JSON.parse(JSON.stringify(e.detail.notebook));
            const simpleDetailWidget = new SimpleNotebookDetailWidget(nb);
            
            app.shell.add(simpleDetailWidget, 'main');
            app.shell.activateById(simpleDetailWidget.id);
            
            // 同时更新信息侧边栏
            simpleInfoSidebar.setNotebookDetail(nb);
          };
          window.addEventListener('galaxy-simple-notebook-selected', handleSimpleNotebookSelected);



        } else {
          // 只支持JSON文件分析
          console.warn('Please select a single JSON file for analysis');
          return;
        }

      } catch (err) {
        console.error('Failed to analyze notebooks:', err);
      } finally {
        isInitializing = false; // 清除初始化标志
      }
    }
  });

  palette.addItem({ command: command, category: 'Galaxy Analysis' });
  palette.addItem({ command: simpleCommand, category: 'Galaxy Analysis' });

  if (restorer) {
    // 已无 tracker，直接不 restore
  }

  app.restored.then(() => {
    // 添加 "Analyze" 按钮到 FileBrowser 工具栏
    const fbWidget = browserFactory.tracker.currentWidget;
    if (fbWidget && fbWidget instanceof FileBrowser) {
      const analyzeButton = new ToolbarButton({
        icon: runIcon,
        tooltip: 'Condition B',
        onClick: () => {
          app.commands.execute(command);
        }
      });

      // 给按钮添加自定义样式，让图标更显眼
      analyzeButton.addClass('galaxy-analyze-button');

      // 直接设置样式确保颜色生效
      setTimeout(() => {
        const iconElement = analyzeButton.node.querySelector('svg');
        if (iconElement) {
          iconElement.style.fill = '#FF6B35';
          iconElement.style.transition = 'all 0.2s ease';

          // 添加悬停效果
          analyzeButton.node.addEventListener('mouseenter', () => {
            if (iconElement) {
              iconElement.style.fill = '#FF4500';
              iconElement.style.transform = 'scale(1.1)';
            }
          });

          analyzeButton.node.addEventListener('mouseleave', () => {
            if (iconElement) {
              iconElement.style.fill = '#FF6B35';
              iconElement.style.transform = 'scale(1)';
            }
          });

          analyzeButton.node.addEventListener('mousedown', () => {
            if (iconElement) {
              iconElement.style.fill = '#FF0000';
              iconElement.style.transform = 'scale(0.95)';
            }
          });

          analyzeButton.node.addEventListener('mouseup', () => {
            if (iconElement) {
              iconElement.style.fill = '#FF4500';
              iconElement.style.transform = 'scale(1.1)';
            }
          });
        }
      }, 100);
      // 添加简化分析按钮
      const simpleAnalyzeButton = new ToolbarButton({
        icon: runIcon,
        tooltip: 'Condition A',
        onClick: () => {
          app.commands.execute(simpleCommand);
        }
      });

      // 给简化分析按钮添加自定义样式
      simpleAnalyzeButton.addClass('galaxy-simple-analyze-button');

      // 直接设置样式确保颜色生效
      setTimeout(() => {
        const iconElement = simpleAnalyzeButton.node.querySelector('svg');
        if (iconElement) {
          iconElement.style.fill = '#28a745';
          iconElement.style.transition = 'all 0.2s ease';

          // 添加悬停效果
          simpleAnalyzeButton.node.addEventListener('mouseenter', () => {
            if (iconElement) {
              iconElement.style.fill = '#20c997';
              iconElement.style.transform = 'scale(1.1)';
            }
          });

          simpleAnalyzeButton.node.addEventListener('mouseleave', () => {
            if (iconElement) {
              iconElement.style.fill = '#28a745';
              iconElement.style.transform = 'scale(1)';
            }
          });

          simpleAnalyzeButton.node.addEventListener('mousedown', () => {
            if (iconElement) {
              iconElement.style.fill = '#1e7e34';
              iconElement.style.transform = 'scale(0.95)';
            }
          });

          simpleAnalyzeButton.node.addEventListener('mouseup', () => {
            if (iconElement) {
              iconElement.style.fill = '#20c997';
              iconElement.style.transform = 'scale(1.1)';
            }
          });
        }
      }, 100);
      fbWidget.toolbar.insertItem(5, 'simpleAnalyzeNotebooks', simpleAnalyzeButton);

      fbWidget.toolbar.insertItem(6, 'analyzeNotebooks', analyzeButton);
    }
  })


  if (app.shell instanceof LabShell) {
    app.shell.layoutModified.connect(() => {
      closeSidebarsIfNoMainWidgets(app);
      // 移除频繁的滚动同步更新
      // updateScrollSync();
    });

    // 检查 notebook detail tab 是否被关闭，并在每次关闭时恢复 overview sidebar
    function checkNotebookDetailWidgetStatus() {
      const mainWidgets = Array.from(app.shell.widgets('main'));
      const currentDetailIds = new Set(
        mainWidgets
          .filter(w => w.id?.startsWith('notebook-detail-widget-'))
          .map(w => w.id!)
      );

      // 检测是否发生变化
      const prevSize = lastKnownDetailIds.size;
      const currSize = currentDetailIds.size;
      const hasChange =
        prevSize !== currSize ||
        [...lastKnownDetailIds].some(id => !currentDetailIds.has(id)) ||
        [...currentDetailIds].some(id => !lastKnownDetailIds.has(id));

      if (!hasChange) {
        return; // 没变化，不处理
      }

      lastKnownDetailIds = currentDetailIds;

      // 检查是否有 detail tab 被关闭，如果有则恢复 overview sidebar
      for (const oldId of notebookDetailIds) {
        if (!currentDetailIds.has(oldId)) {
          // Track notebook closing immediately when we detect the closure

          // Try to find the widget before it's completely removed
          const allWidgets = [
            ...Array.from(app.shell.widgets('main')),
            ...Array.from(app.shell.widgets('left')),
            ...Array.from(app.shell.widgets('right'))
          ];
          const closedWidget = allWidgets.find(w => w.id === oldId);

          if (closedWidget) {
            const notebookData = (closedWidget as any).notebook;
            if (notebookData) {
              analytics.trackNotebookClosed(
                notebookData.kernelVersionId || `nb_${notebookData.index || Date.now()}`,
                {
                  tabTitle: closedWidget.title?.label,
                  tabId: closedWidget.id
                }
              );
            }
          } else {
            // Widget has been completely removed, which is expected behavior
            // Even if widget is removed, try to track the closure using the ID
            analytics.trackNotebookClosed(
              oldId.replace('notebook-detail-widget-', ''),
              {
                tabTitle: oldId,
                tabId: oldId
              }
            );
          }


          // 当 notebook detail widget 被关闭时，立即恢复 overview sidebar
          if (result1 && matrixWidget && detailSidebar) {

            // 先清理现有的左侧 sidebar
            const leftWidgets = Array.from(app.shell.widgets('left'));
            for (const w of leftWidgets) {
              if (w.id === 'flow-chart-widget') w.close();
            }

            // 重新创建或恢复 flowChartWidget
            if (!flowChartWidget || flowChartWidget.isDisposed) {
              flowChartWidget = new LeftSidebar(result1, colorMap, true); // Overview mode
            } else {
              flowChartWidget.setData(result1, colorMap);
            }

            app.shell.add(flowChartWidget, 'left');
            app.shell.activateById(flowChartWidget.id);

            const { mostFreqStage, mostFreqFlow } = flowChartWidget.getMostFrequentStageAndFlow();

            // 检查detailSidebar是否已经在右侧
            const rightWidgets = Array.from(app.shell.widgets('right'));
            const isAlreadyInRight = rightWidgets.includes(detailSidebar);

            // 先恢复状态
            detailSidebar.setFilter(null);
            detailSidebar.setSummary(result1, mostFreqStage, mostFreqFlow, matrixWidget.getNotebookOrder());

            // 如果不在右侧才添加，避免重复触发onAfterAttach
            if (!isAlreadyInRight) {
              app.shell.add(detailSidebar, 'right');
            }
            app.shell.activateById(detailSidebar.id);

            // 确保overview状态正确显示，延迟调用以覆盖可能的restoreDetailFilterState
            setTimeout(() => {
              if (detailSidebar && matrixWidget) {
                detailSidebar.setSummary(result1, mostFreqStage, mostFreqFlow, matrixWidget.getNotebookOrder());
              }
            }, 0);

            // 确保matrix widget可见并激活
            if (matrixWidget && !matrixWidget.isVisible) {
              app.shell.activateById(matrixWidget.id);
            }
          }

          // 更新滚动同步状态
          updateScrollSync();
        }
      }

      // 更新记录
      notebookDetailIds.clear();
      for (const id of currentDetailIds) {
        notebookDetailIds.add(id);
      }
    }
    // 只在 layoutModified 里检测，不在 currentChanged/activeChanged 里检测
    app.shell.layoutModified.connect(() => {
      checkNotebookDetailWidgetStatus();
      // 检查是否有分屏布局
      if (hasSplitLayout()) {
        // 收缩左右sidebar而不是关闭
        if (typeof (app.shell as any).collapseLeft === 'function') {
          (app.shell as any).collapseLeft();
        }
        if (typeof (app.shell as any).collapseRight === 'function') {
          (app.shell as any).collapseRight();
        }
      }
      // 在布局变化时更新滚动同步状态
      setTimeout(() => updateScrollSync(), 100);
    });
    // 用 MutationObserver 动态绑定 tab click delegate，保证 MyBinder/JupyterLab 任何时机都能绑定
    function bindTabClickDelegates() {
      document.querySelectorAll('.lm-TabBar-content').forEach(tabBar => {
        if (!(tabBar as any).__galaxyClickBound) {
          tabBar.addEventListener('click', (e) => {
            let target = e.target as HTMLElement;
            while (target && !target.classList.contains('lm-TabBar-tab') && target !== tabBar) {
              target = target.parentElement as HTMLElement;
            }
            if (target && target.classList.contains('lm-TabBar-tab')) {
              const dataId = target.getAttribute('data-id');
                      // 通过 data-id 找到 widget
              const allWidgets = [
                ...Array.from(app.shell.widgets('main')),
                ...Array.from(app.shell.widgets('left')),
                ...Array.from(app.shell.widgets('right'))
              ];
              const widget = allWidgets.find(w => w.id === dataId);
              if (widget) {
                handleTabSwitch(widget);
              }
            }
          });
          (tabBar as any).__galaxyClickBound = true;
        }
      });
    }
    const observer = new MutationObserver(bindTabClickDelegates);
    observer.observe(document.body, { childList: true, subtree: true });
    bindTabClickDelegates(); // 初始绑定

    // 监听 tab 关闭按钮，打印 notebook detail tab 被关闭的日志
    function bindTabCloseDelegates() {
      document.querySelectorAll('.lm-TabBar-content').forEach(tabBar => {
        if (!(tabBar as any).__galaxyCloseBound) {
          tabBar.addEventListener('click', (e) => {
            const target = e.target as HTMLElement;
            if (target && target.classList.contains('lm-TabBar-tabCloseIcon')) {
              const tabElement = target.closest('.lm-TabBar-tab');
              if (tabElement) {
                const dataId = tabElement.getAttribute('data-id');
                if (dataId && dataId.startsWith('simple-notebook-detail-widget-')) {
                  // 触发事件通知SimpleInfoSidebar清除notebook信息
                  window.dispatchEvent(new CustomEvent('galaxy-simple-notebook-detail-closed'));
                } else if (dataId && dataId === 'simple-notebook-list-widget') {
                  // Simple notebook list widget is being closed
                  // Close simple info sidebar when list is closed
                  setTimeout(() => {
                    const rightWidgets = Array.from(app.shell.widgets('right'));
                    for (const rightWidget of rightWidgets) {
                      if (rightWidget.id === 'simple-info-sidebar') {
                        rightWidget.close();
                      }
                    }
                  }, 100);
                }
              }
            }
          });
          (tabBar as any).__galaxyCloseBound = true;
        }
      });
    }
    bindTabCloseDelegates();
    const closeObserver = new MutationObserver(bindTabCloseDelegates);
    closeObserver.observe(document.body, { childList: true, subtree: true });

    // 监听 main 区域 widget 的 disposed 事件，主要用于日志记录
    function monitorMainWidgetDisposed() {
      const mainWidgets = Array.from(app.shell.widgets('main'));

      for (const w of mainWidgets) {
        if (!(w as any).__galaxyDisposedBound) {
          w.disposed.connect(() => {
            // Track notebook closing if it's a notebook detail widget
            if (w.id && w.id.startsWith('notebook-detail-widget-')) {
              // Get notebook data for analytics tracking
              const notebookData = (w as any).notebook;
              if (notebookData) {
                analytics.trackNotebookClosed(
                  notebookData.kernelVersionId || `nb_${notebookData.index || Date.now()}`,
                  {
                    tabTitle: w.title?.label,
                    tabId: w.id
                  }
                );
              }

              // 对于notebook detail widget的关闭，延迟处理以确保状态稳定
              setTimeout(() => {
                const widget = getActiveGalaxyWidget();
                if (widget) {
                  handleTabSwitch(widget);
                } else {
                  closeSidebarsIfNoMainWidgets(app);
                }
              }, 200); // 增加延迟时间，确保状态稳定
            } else if (w.id && w.id.startsWith('simple-notebook-detail-widget-')) {
              // Simple notebook detail widget was closed
              // 触发事件通知SimpleInfoSidebar清除notebook信息
              window.dispatchEvent(new CustomEvent('galaxy-simple-notebook-detail-closed'));
              
              // 延迟处理以确保状态稳定
              setTimeout(() => {
                const widget = getActiveGalaxyWidget();
                if (widget) {
                  handleTabSwitch(widget);
                }
              }, 100);
            } else if (w.id === 'matrix-widget') {
              // Matrix widget (overview) was closed

              // Close sidebars when overview is closed
              setTimeout(() => {
                closeSidebarsIfNoMainWidgets(app);
              }, 100);
            } else if (w.id === 'simple-notebook-list-widget') {
              // Simple notebook list widget was closed
              // Close simple info sidebar when list is closed
              setTimeout(() => {
                const rightWidgets = Array.from(app.shell.widgets('right'));
                for (const rightWidget of rightWidgets) {
                  if (rightWidget.id === 'simple-info-sidebar') {
                    rightWidget.close();
                  }
                }
              }, 100);
            } else {
              setTimeout(() => {
                const widget = getActiveGalaxyWidget();
                if (widget) {
                  handleTabSwitch(widget);
                }
              }, 100);
            }
          });
          (w as any).__galaxyDisposedBound = true;
        }
      }
    }
    // 初始绑定
    monitorMainWidgetDisposed();
    // 每次 tab 切换后重新绑定（因为新 widget 可能被添加）
    app.shell.currentChanged.connect(() => {
      setTimeout(() => {
        monitorMainWidgetDisposed();
      }, 0);
    });

    // 监听滚动同步锁定状态变化
    window.addEventListener('galaxy-scroll-sync-update', (e: Event) => {
      const customEvent = e as CustomEvent;
      const { widgetId, locked } = customEvent.detail;
      if (locked) {
        lockedWidgets.add(widgetId);
      } else {
        lockedWidgets.delete(widgetId);
      }
    });
  }
}

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'galaxy:plugin',
  description: 'Analyze selected notebooks and show Sankey diagram.',
  autoStart: true,
  requires: [ICommandPalette, IFileBrowserFactory],
  optional: [ILayoutRestorer],
  activate
};

export default plugin;