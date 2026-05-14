import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei'] # 接受中文
# 设置默认坐标轴字体大小，后面也有单独设置，但是有时候对指数不起作用，所用这里先设个默认值
plt.rcParams['font.size'] = 18 
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import FormatStrFormatter
from matplotlib import ticker
import numpy as np
import seaborn as sns
from web3 import Web3
import json
import os

# 通过合约获取每个叶节点上的资源数量，保存在excle文件中
def statisticsResourceNumberOnLeafNode(contractAddress, contractABI, file_path_result, clumnNameCount, clumnNameLayer):
    # 连接Ganache:
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
    # print(w3.isConnected())

    # 获取最新区块号（区块高度）
    print('blockNumber is: %d' % w3.eth.blockNumber)
    ''''''
    # 获取合约接口
    CAKE_BSC_ADDRESS = Web3.toChecksumAddress(contractAddress)
    with open(contractABI, 'r') as f:
        CAKE_BSC_ABI  = json.load(f)

    token_contract = w3.eth.contract(address=CAKE_BSC_ADDRESS, abi=CAKE_BSC_ABI)

    # 设置默认账户，就是发起交易的地址
    w3.eth.defaultAccount = w3.eth.accounts[5]

    # 从磁盘读取结果存放文件，如果不存在就新建
    if(os.path.isfile(file_path_result)==False):
        df=pd.DataFrame()
        df.to_excel(file_path_result)
    data = pd.read_excel(file_path_result, sheet_name='Sheet1')
    ''''''
    nodeCount = token_contract.functions.getSumTokenTreeNode().call()
    count = 0
    # 获取叶节点上附着token的数量
    for i in range(1, nodeCount):
        # 获取节点，此处node为元组tuple类型
        node = token_contract.functions.getTheTokenTreeNode(i).call()
        if len(node[1]) == 0:  # node没有子节点，即为叶节点   如果是quad tree，改为node[1] == [0, 0, 0, 0]判断叶节点
            tokenCount = token_contract.functions.getTokenIDList(i).call()
            # 写叶节点上附着token的数量和叶节点所在层数
            data.loc[count, clumnNameCount] = len(tokenCount)
            data.loc[count, clumnNameLayer] = node[3]
            count += 1

    pd.DataFrame(data).to_excel(file_path_result, index=False)

# 使用seaborn库绘制叶节点容量使用率密度分布图
def drawCalculatedRatioOfLeafNode(file_path):

    fig1 = plt.figure(1)
    ax1 = fig1.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.12, right=0.99, top=0.95, bottom=0.15)
    fig2 = plt.figure(2)
    ax2 = fig2.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.12, right=0.99, top=0.95, bottom=0.15)

    frontsize = 20
    font1 = {'size': frontsize}
    font2 = {'size': 18}
    legend = ['Proposed FBSI', 'Quad-Tree', 'Proposed FBSI', 'Proposed FBSI', 'Quad-Tree', 'Quad-Tree']
    color = [(31 / 255, 50 / 255, 255 / 255), (255 / 255, 100 / 255, 14 / 255)]
    
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    sns.histplot(data['NormallyFBSITokenCount'], bins=11, binrange=(0, 11), stat='density', kde=False, alpha=0.7, ax=ax1)# hatch='xx', 
    sns.kdeplot(data['NormallyFBSITokenCount'], color=color[0], linewidth=2.5, ax=ax1)# color=color[0],
    # ax1.lines[-1].set_linestyle('--')  # stat='density'   stat='percent'  line_kws={'linestyle': '--'}
    print('alpha FBSI normal:', np.mean(data['NormallyFBSITokenCount']))

    sns.histplot(data['NormallyQuadTokenCount'], bins=11, binrange=(0, 11), stat='density', kde=False, alpha=0.2, ax=ax1)# hatch='/',
    sns.kdeplot(data['NormallyQuadTokenCount'], color=color[1], linewidth=2.5, ax=ax1)# color=color[1],
    # ax1.lines[-1].set_linestyle('--')  # stat='density'   stat='percent'  line_kws={'linestyle': '--'}
    print('alpha-quad normal:', np.mean(data['NormallyQuadTokenCount']))

    # ax1.legend(legend, loc='upper left', prop=font2)
    ax1.set_xlabel('叶节点饱和度（%）（正态分布）', font1)
    ax1.set_ylabel('叶节点数量百分比（%）', font1)
    ax1.set_xticks(np.linspace(0.5, 10.5, 11), range(0, 110, 10), size=frontsize)
    ax1.set_yticks(np.linspace(0, 0.30, 7), range(0, 31, 5), size=frontsize)
    ax1.set_xlim(-0.5, 11.5)
    ax1.set_ylim(0, 0.29)
    # plt.show()
    
    sns.histplot(data['UniformFBSITokenCount'], bins=11, binrange=(0, 11), stat='density', kde=False, alpha=0.7, ax=ax2)# hatch='xx',
    sns.kdeplot(data['UniformFBSITokenCount'], color=color[0], linewidth=2.5, ax=ax2)# color=color[0],
    # 设置拟合线为虚线
    # ax2.lines[-1].set_linestyle('--')  # stat='density'   stat='percent'  line_kws={'linestyle': '--'}
    print('alpha FBSI uniform :', np.mean(data['UniformFBSITokenCount']))

    sns.histplot(data['UniformQuadTokenCount'], bins=11, binrange=(0, 11), stat='density', kde=False, alpha=0.2, ax=ax2)# hatch='/',
    sns.kdeplot(data['UniformQuadTokenCount'], color=color[1], linewidth=2.5,  ax=ax2)# color=color[1],
    # 设置拟合线为虚线
    # ax2.lines[-1].set_linestyle('--')  # stat='density'   stat='percent'  line_kws={'linestyle': '--'}
    print('alpha quad uniform :', np.mean(data['UniformQuadTokenCount']))

    # ax2.legend(legend, loc='upper left', prop=font2)
    ax2.set_xlabel('叶节点饱和度（%）（均匀分布）', font1)
    ax2.set_ylabel('叶节点数量百分比（%）', font1)
    ax2.set_xticks(np.linspace(0.5, 10.5, 11), range(0, 110, 10), size=frontsize)
    ax2.set_yticks(np.linspace(0, 0.25, 6), range(0, 26, 5), size=frontsize)
    ax2.set_xlim(-0.5, 11.5)
    ax2.set_ylim(0, 0.29)
    plt.show()

# 使用seaborn库绘制构建树形结构中节点分裂时间直方图（含概率密度分布曲线）
def drawBuildResultOfSplitTime(file_path_list):
    startnum = 0
    endnum = 2500

    colorlist = [(214 / 255, 39 / 255, 40 / 255), (44 / 255, 160 / 255, 44 / 255),
                 (31 / 255, 119 / 255, 180 / 255), (255 / 255, 127 / 255, 14 / 255), 'k', 'tan', 'darkorange',
                 'aquamarine', 'm', 'navy']
    markerlist = ['3', '3', '4', '4', '.', '.', '+', '+', 'x', 'x']
    
    # 创建画板
    frontsize = 20
    fig1 = plt.figure(1)
    ax1 = fig1.add_subplot(1, 1, 1)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    plt.subplots_adjust(left=0.12, right=0.98, top=0.95, bottom=0.15)
    
    fig2 = plt.figure(2)
    ax2 = fig2.add_subplot(1, 1, 1)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    plt.subplots_adjust(left=0.12, right=0.98, top=0.95, bottom=0.15)
    
    subplot = [ax1, ax2]

    font1 = {'size': 18}
    legend = ['Proposed FBSI', 'Quad-Tree']
    # 亮蓝，橙色
    color = [(31 / 255, 50 / 255, 255 / 255), (255 / 255, 100 / 255, 14 / 255)]

    tokenID_list = []
    node_count_list = []
    alpha = [0.7, 0.2]
    hatch = ['xx', '/']
    for i in range(0, len(file_path_list)):
        file_path = file_path_list[i]
        data = pd.read_excel(file_path, sheet_name='Sheet1')
        tokenID = data['tokenID'][startnum:endnum]
        time_start = data['time_start'][startnum:endnum]
        time_end = data['time_end'][startnum:endnum]
        node_count = data['node_count'][startnum:endnum]

        temptime = time_end - time_start
        data['time_diff']=temptime
        pd.DataFrame(data).to_excel(file_path, index=False)
        # 确定分裂点，保留分裂点的分裂时间
        temptime = temptime.tolist()
        timeSplit = []
        timeUnSplit = []
        for k in range(1, len(temptime)):
            if node_count[k]>node_count[k-1]:
                timeSplit.append(temptime[k])
            else:
                timeUnSplit.append(temptime[k])

        # 绘制节点分裂时间直方图  hatch=hatch[int(i%2)], color=color[int(i % 2)],color=colorlist[int(i % 2)],
        # 统计直方图+拟合曲线，前两个Excel数据绘制在同一幅，后两个绘制在同一幅
        # sns.histplot(time, bins=20, binrange=(1.5,5.0), stat='probability', kde=True, alpha=0.5, legend=True, ax=subplot[int(i/2)])
        # 统计直方图，前两个Excel数据绘制在同一幅，后两个绘制在同一幅
        sns.histplot(timeSplit, bins=15, binrange=(0.5, 5.0), stat='density', kde=False, alpha=alpha[int(i%2)], ax=subplot[int(i/2)])
        # 分裂时间拟合曲线，前两个Excel数据绘制在同一幅，后两个绘制在同一幅
        sns.kdeplot(timeSplit, color=color[int(i % 2)], linewidth=2.5, ax=subplot[int(i/2)])
        # subplot[int(i / 2)].lines[-1].set_linestyle('--')  # stat='density' stat='percent' stat='probability' line_kws={'linestyle': '--'},
        print("平均分裂时间：", np.mean(timeSplit))

    # fig1.subplots_adjust(hspace=0.5)
    ax1.set_xlabel('节点分裂时间（s）（正态分布）', size=frontsize)
    ax1.set_ylabel('节点占比（%）', size=frontsize)
    ax1.set_xlim(0.5, 5.0)
    ax1.set_yticks(np.linspace(0, 1.2, 8), range(0, 36, 5))
    ax1.set_ylim(0.0, 1.3)
    # ax1.legend(legend, loc='upper right', prop=font1)

    ax2.set_xlabel('节点分裂时间（s）（均匀分布）', size=frontsize)
    ax2.set_ylabel('节点占比（%）', size=frontsize)
    ax2.set_xlim(0.5, 5.0)
    ax2.set_yticks(np.linspace(0, 1.2, 8), range(0, 36, 5))
    ax2.set_ylim(0.0, 1.3)
    # ax2.legend(legend, loc='upper right', prop=font1)

    # 显示图像
    plt.show()

# 使用seaborn库绘制构建树形结构的节点-资源数关系图
def drawBuildResultOfNodeToData(file_path_list):
    startnum = 0
    endnum = 2500

    colorlist = [(31 / 255, 120 / 255, 180 / 255), (255 / 255, 127 / 255, 0 / 255),
                 (255 / 255, 127 / 255, 14 / 255), (31 / 255, 119 / 255, 180 / 255),'k', 'tan', 'darkorange',
                 'aquamarine', 'm', 'navy']
    markerlist = ['3', '3', '4', '4', '.', '.', '+', '+', 'x', 'x']
    
    # 创建画板
    frontsize = 20
    fig3 = plt.figure(3)
    ax3 = fig3.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.14, right=0.99, top=0.94, bottom=0.15)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    
    fig4 = plt.figure(4)
    ax4 = fig4.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.14, right=0.99, top=0.94, bottom=0.15)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    
    subplot2 = [ax3, ax4]

    font1 = {'size': 18}
    legend = ['Proposed FBSI', 'Quad-Tree']
    # 亮蓝，橙色
    color = [(31 / 255, 50 / 255, 255 / 255), (255 / 255, 100 / 255, 14 / 255)]

    tokenID_list = []
    node_count_list = []
    alpha = [0.7, 0.2]
    hatch = ['xx', '/']
    for i in range(0, len(file_path_list)):
        file_path = file_path_list[i]
        data = pd.read_excel(file_path, sheet_name='Sheet1')
        tokenID = data['tokenID'][startnum:endnum]
        node_count = data['node_count'][startnum:endnum]

        # 节点-资源数关系图
        # 删除资源数量增加但节点不增的数据
        tokenID = tokenID.tolist()
        node_count = node_count.tolist()
        j = 1
        while j < len(tokenID):
            if node_count[j] > 510:
                tokenID.pop(j)
                node_count.pop(j)
                continue
            if node_count[j - 1] == node_count[j]:
                tokenID.pop(j - 1)
                node_count.pop(j - 1)
            else:
                j += 1
        tokenID_list.append(tokenID)
        node_count_list.append(node_count)
        # 绘制节点数据-资源数量关系图
        subplot2[int(i/2)].plot(node_count, tokenID, color=colorlist[int(i % 2)], alpha=0.8)

    ax3.fill_between(node_count_list[0], tokenID_list[0], 0,  # 上限，下限
                     facecolor=colorlist[3],  # 填充颜色
                     alpha=0.2)  # 透明度
    ax3.fill_between(node_count_list[1], tokenID_list[1], 0,  # 上限，下限
                     facecolor=colorlist[2],  # 填充颜色
                     alpha=0.2)  # 透明度
    ax3.set_xlabel('节点数量（正态分布）', size=frontsize)
    ax3.set_ylabel('数据量', size=frontsize) # 'Number of Resources'
    ax3.set_xlim(0, 520)
    ax3.set_ylim(0, 2700)
    ax3.ticklabel_format(style='sci', scilimits=(0,0), axis='y')
    formatter = ticker.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((0,0))
    ax3.yaxis.set_major_formatter(formatter)

    ax3.legend(legend, prop=font1)
    print('数据容量-normal-FBSI：', tokenID_list[0][len(tokenID_list[0])-1])
    print('数据容量-normal-quad：', tokenID_list[1][len(tokenID_list[1]) - 1])

    ax4.fill_between(node_count_list[2], tokenID_list[2], 0,  # 上限，下限
                     facecolor=colorlist[3],  # 填充颜色
                     alpha=0.2)  # 透明度
    ax4.fill_between(node_count_list[3], tokenID_list[3], 0,  # 上限，下限
                     facecolor=colorlist[2],  # 填充颜色
                     alpha=0.2)  # 透明度
    ax4.set_xlabel('节点数量（均匀分布）', size=frontsize)
    ax4.set_ylabel('数据量', size=frontsize)# 'Number of Resources'
    ax4.set_xlim(0, 520)
    ax4.set_ylim(0, 2700)
    ax4.yaxis.set_major_formatter(formatter)

    ax4.legend(legend, prop=font1)
    print('数据容量-uniform-FBSI：', tokenID_list[2][len(tokenID_list[2]) - 1])
    print('数据容量-uniform-quad：', tokenID_list[3][len(tokenID_list[3]) - 1])

    # 显示图像
    # plt.rc('font', size=18)
    plt.show()

# 分析节点分裂的插入数据gas cost与资源数量的关系
def drawBuildTreeGasCostSplit(file_path_list):
    
    startnum = 0
    endnum = 2500
    baseGas = [244102, 244560] # 无索引方案正态和均匀分布的平均插入gas开销

    # 创建画板
    frontsize = 20
    frontsize2 = 17
    fig1 = plt.figure(1)
    ax1 = fig1.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.15, right=0.99, top=0.94, bottom=0.15)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    fig2 = plt.figure(2)
    ax2 = fig2.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.15, right=0.99, top=0.94, bottom=0.15)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    subplot = [ax1, ax2]

    font1 = {'size': 18}
    alpha = [0.7, 0.2]
    color = [(31 / 255, 120 / 255, 180 / 255), (255 / 255, 127 / 255, 0 / 255)]

    for i in range(0, len(file_path_list)):
        file_path = file_path_list[i]
        data = pd.read_excel(file_path, sheet_name='Sheet1')
        tokenID = data['tokenID'][startnum:endnum].tolist()
        # 减掉无索引的基础插入gas
        # gasUsed = (data['gasUsed'][startnum:endnum]-baseGas[int(i/2)]).tolist()
        gasUsed = data['gasUsed'][startnum:endnum].tolist()
        node_count = data['node_count'][startnum:endnum].tolist()

        # 分裂点的gasUsed和tokenID
        gasUsedSplit = []
        tokenIDSplit = []

        j = 1
        while j<len(tokenID):
            if node_count[j-1]<node_count[j]:
                gasUsedSplit.append(gasUsed[j])
                tokenIDSplit.append(tokenID[j])
            j += 1

        # 绘制gasUsed线图，前两个Excel数据绘制在同一幅，后两个绘制在同一幅
        subplot[int(i/2)].plot(tokenIDSplit,gasUsedSplit,color=color[int(i%2)],lw=1.5)
        # 绘制gasUsed统计直方图，前两个Excel数据绘制在同一幅，后两个绘制在同一幅 binrange=(0.5, 5.0), 
        # sns.histplot(gasUsedSplit, bins=25, binrange=(0, 3500000), stat='percent', kde=False, alpha=alpha[int(i%2)], ax=subplot[int(i/2)])
        # sns.histplot(gasUsedUnSplit, bins=25, binrange=(220000, 400000), stat='percent', kde=False, alpha=alpha[int(i%2)], ax=subplot2[int(i/2)])
        # 绘制gasUsed拟合曲线，前两个Excel数据绘制在同一幅，后两个绘制在同一幅
        # sns.kdeplot(gasUsedSplit, linewidth=2.5, ax=subplot[int(i/2)])
        # sns.kdeplot(gasUsedUnSplit, linewidth=2.5, ax=subplot2[int(i/2)])

        print('节点分裂的平均gas cost: ', np.mean(gasUsedSplit))
    
    '''折线图的坐标轴设置'''
    legend = ['Proposed FBSI', 'Quad-Tree']
    # ax1.set_title('Gas Cost of Inserting Data with Node Spliting (Normal)')
    ax1.set_xlabel('数据量（正态分布）', size=frontsize)
    ax1.set_ylabel('数据上链gas开销（节点分裂）', size=frontsize)
    ax1.legend(legend, loc='upper right', prop=font1)
    ax1.set_yticks(range(0, 3600000, 500000))
    ax1.set_ylim(200000,3400000)
    formatter = ticker.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((0,0))
    ax1.yaxis.set_major_formatter(formatter)
    

    # ax2.set_title('Gas Cost of Inserting Data with Node Spliting (Uniform)')
    ax2.set_xlabel('数据量（均匀分布）', size=frontsize)
    ax2.set_ylabel('数据上链gas开销（节点分裂）', size=frontsize)
    ax2.legend(legend, loc='upper right', prop=font1)
    ax2.set_yticks(range(0, 3100000, 500000))
    ax2.yaxis.set_major_formatter(formatter)
    ax2.set_ylim(200000,2600000)

    # 用科学计数法表示坐标轴
    # style='sci' 指明用科学记数法，scilimits=(-1,2) 表示对（10^-1,10^2）范围之外的值换科学记数法，范围内的数不换
    # ax4.ticklabel_format(style='sci', scilimits=(1,2), axis='both')
    plt.rc('font', size=18)
    plt.show()

# 分析未发生节点分裂时的插入数据gas cost与资源数量的关系
def drawBuildTreeGasCostUnsplit(file_path_list):
    
    startnum = 0
    endnum = 2500

    # 创建画板
    frontsize = 20
    frontsize2 = 17

    fig3 = plt.figure(3)
    ax3 = fig3.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.17, right=0.99, top=0.94, bottom=0.15)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    fig4 = plt.figure(4)
    ax4 = fig4.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.17, right=0.99, top=0.94, bottom=0.15)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    subplot2 = [ax3, ax4]

    font1 = {'size': 18}
    alpha = [0.7, 0.2]
    color = [(31 / 255, 120 / 255, 180 / 255), (255 / 255, 127 / 255, 0 / 255)]

    for i in range(0, len(file_path_list)):
        file_path = file_path_list[i]
        data = pd.read_excel(file_path, sheet_name='Sheet1')
        tokenID = data['tokenID'][startnum:endnum].tolist()
        gasUsed = data['gasUsed'][startnum:endnum].tolist()
        node_count = data['node_count'][startnum:endnum].tolist()

        # 非分裂gasUsed和tokeID
        gasUsedUnSplit = []
        tokenIDUnSplit = []

        gasUsedUnSplit.append(gasUsed[0])
        tokenIDUnSplit.append(tokenID[0])

        j = 1
        while j<len(tokenID):
            if node_count[j-1] == node_count[j]:
                gasUsedUnSplit.append(gasUsed[j])
                tokenIDUnSplit.append(tokenID[j])
            j += 1
        
        # 对不发生节点分裂的数据插入结果抽稀
        sparse_tokenIDUnSplit = []
        sparse_gasUsedUnSplit = []
        skip = 3 
        s = 1
        while s<len(tokenIDUnSplit):
            sparse_tokenIDUnSplit.append(tokenIDUnSplit[s])
            sparse_gasUsedUnSplit.append(gasUsedUnSplit[s])
            s = s+skip

        # 绘制gasUsed线图，前两个Excel数据绘制在同一幅，后两个绘制在同一幅
        subplot2[int(i/2)].plot(sparse_tokenIDUnSplit,sparse_gasUsedUnSplit,color=color[int(i%2)],lw=1)
        # 绘制gasUsed统计直方图，前两个Excel数据绘制在同一幅，后两个绘制在同一幅 binrange=(0.5, 5.0), 
        # sns.histplot(gasUsedSplit, bins=25, binrange=(0, 3500000), stat='percent', kde=False, alpha=alpha[int(i%2)], ax=subplot[int(i/2)])
        # sns.histplot(gasUsedUnSplit, bins=25, binrange=(220000, 400000), stat='percent', kde=False, alpha=alpha[int(i%2)], ax=subplot2[int(i/2)])
        # 绘制gasUsed拟合曲线，前两个Excel数据绘制在同一幅，后两个绘制在同一幅
        # sns.kdeplot(gasUsedSplit, linewidth=2.5, ax=subplot[int(i/2)])
        # sns.kdeplot(gasUsedUnSplit, linewidth=2.5, ax=subplot2[int(i/2)])

        print('节点未分裂的平均gas cost: ', np.mean(gasUsedUnSplit))
    
    '''折线图的坐标轴设置'''
    legend = ['Proposed FBSI', 'Quad-Tree']
    
    # ax3.set_title('Gas Cost of Inserting Data with Node Non-Spliting (Normal)')
    ax3.set_xlabel('数据量（正态分布）', size=frontsize)
    ax3.set_ylabel('数据上链gas开销（无节点分裂）', size=frontsize)
    ax3.legend(legend, loc='lower right', prop=font1)
    # 科学计数法 e为底
    # ax3.ticklabel_format(style='sci', scilimits=(1,2), axis='both') 
    # 科学计数法 10为底
    formatter = ticker.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((0,0))
    ax3.yaxis.set_major_formatter(formatter)
    ax3.set_ylim(216000,385000)

    # ax4.set_title('Gas Cost of Inserting Data with Node Non-Spliting (Uniform)')
    ax4.set_xlabel('数据量（均匀分布）', size=frontsize)
    ax4.set_ylabel('数据上链gas开销（无节点分裂）', size=frontsize)
    ax4.legend(legend, loc='lower right', prop=font1)
    ax4.yaxis.set_major_formatter(formatter)
    ax4.set_ylim(216000,385000)

    # 用科学计数法表示坐标轴
    # style='sci' 指明用科学记数法，scilimits=(-1,2) 表示对（10^-1,10^2）范围之外的值换科学记数法，范围内的数不换
    # ax4.ticklabel_format(style='sci', scilimits=(1,2), axis='both')
    plt.rc('font', size=18)
    plt.show()

# 分批注入2500个资源数据，每500个时执行一组（50）个查询，绘制查询时间柱状图
def drawQueryTimeMaxMinMean(file_path_list1, file_path_list2):
    frontsize = 20
    font1 = {'size': frontsize}
    font2 = {'size': 18}
    legend = ['Proposed FBSI', 'Quad-Tree']
    color = [(98 / 255, 159 / 255, 202 / 255), (255 / 255, 229 / 255, 206 / 255)]
    # 创建画板1，显示正态分布的构建时间
    fig1 = plt.figure(1)  # 如果不传入参数默认画板1
    ax1 = fig1.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.15, right=0.99, top=0.95, bottom=0.15)
    plt.yticks(fontsize=frontsize)
    ax1.set_xlabel('数据量（正态分布）', size=frontsize)
    ax1.set_ylabel('平均时间（s）', size=frontsize)

    fig2 = plt.figure(2)
    ax2 = fig2.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.15, right=0.99, top=0.95, bottom=0.15)
    plt.yticks(fontsize=frontsize)
    ax2.set_xlabel('数据量（均匀分布）', size=frontsize)
    ax2.set_ylabel('平均时间（s）', size=frontsize)

    colorlist = [(214 / 255, 39 / 255, 40 / 255), (44 / 255, 160 / 255, 44 / 255),
                 (31 / 255, 119 / 255, 180 / 255), (255 / 255, 127 / 255, 14 / 255), 'k', 'tan', 'darkorange',
                 'aquamarine', 'm', 'navy']


    E_time = []
    for i in range(0, len(file_path_list1)):
        AccTime = []
        for k in range(0, len(file_path_list1[i])):
            file_path = file_path_list1[i][k]
            data = pd.read_excel(file_path, sheet_name='Sheet1')
            time_start = data['time_start']
            time_end = data['time_end']
            # 处理时间数据
            time = time_end - time_start
            time = time.tolist()
            AccTime.append(np.mean(time))
        E_time.append(AccTime)

    print(E_time)

    Q_time = []
    for i in range(0, len(file_path_list2)):
        AccTime = []
        for k in range(0, len(file_path_list2[i])):
            file_path = file_path_list2[i][k]
            data = pd.read_excel(file_path, sheet_name='Sheet1')
            time_start = data['time_start']
            time_end = data['time_end']
            # 处理时间数据
            time = time_end - time_start
            time = time.tolist()
            AccTime.append(np.mean(time))
        Q_time.append(AccTime)

    print(Q_time)

    print('平均查询时间（FBSI normal）：', np.mean(E_time[0]))
    print('平均查询时间（quad normal）：', np.mean(Q_time[0]))
    print('平均查询时间（FBSI uniform）：', np.mean(E_time[1]))
    print('平均查询时间（quad uniform）：', np.mean(Q_time[1]))

    data_x = [500, 1000, 1500, 2000, 2500]
    
    # 柱状图
    x = np.arange(5)  # x轴刻度标签位置
    width = 0.4  # 柱子的宽度

    # 计算每个柱子在x轴上的位置，保证x轴刻度标签居中
    ax1.bar(x - 0.5 * width, E_time[0], width, color=color[0], edgecolor='k', hatch='xx', alpha=1)
    ax1.bar(x + 0.5 * width, Q_time[0], width, color=color[1], edgecolor='k', hatch='/', alpha=1)
    ax1.set_ylim(0.0, 1.0)
    ax1.set_xticks(x, labels=data_x, size=frontsize)
    ax1.legend(legend, loc='upper left', prop=font2)

    ax2.bar(x - 0.5 * width, E_time[1], width, color=color[0], edgecolor='k', hatch='xx', alpha=1)
    ax2.bar(x + 0.5 * width, Q_time[1], width, color=color[1], edgecolor='k', hatch='/', alpha=1)
    ax2.set_ylim(0.0, 1.0)
    ax2.set_xticks(x, labels=data_x, size=frontsize)
    ax2.legend(legend, loc='upper left', prop=font2)

    plt.show()

# 分批注入2500个资源数据，每500个时执行一组（50）个查询，绘制查询gas cost柱状图
def drawQueryMaxMinMeanGasCost(file_path_list1, file_path_list2):
    frontsize = 20
    font2 = {'size': 18}
    legend = ['Proposed FBSI', 'Quad-Tree']
    color = [(98 / 255, 159 / 255, 202 / 255), (255 / 255, 229 / 255, 206 / 255)]
    # 创建画板1，显示正态分布的构建时间
    fig1 = plt.figure(1)  # 如果不传入参数默认画板1
    ax1 = fig1.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.10, right=0.99, top=0.94, bottom=0.15)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    ax1.set_xlabel('数据量（正态分布）', size=frontsize)
    ax1.set_ylabel('平均gas开销', size=frontsize)

    fig2 = plt.figure(2)
    ax2 = fig2.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.10, right=0.99, top=0.94, bottom=0.15)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    ax2.set_xlabel('数据量（均匀分布）', size=frontsize)
    ax2.set_ylabel('平均gas开销', size=frontsize)

    E_Gas = []
    for i in range(0, len(file_path_list1)):
        AccGas = []
        for k in range(0, len(file_path_list1[i])):
            file_path = file_path_list1[i][k]
            data = pd.read_excel(file_path, sheet_name='Sheet1')
            gasUsed = data['gasUsed'].tolist()
            AccGas.append(np.mean(gasUsed))
        E_Gas.append(AccGas)

    print(E_Gas)    

    Q_Gas = []
    for i in range(0, len(file_path_list2)):
        AccGas = []
        for k in range(0, len(file_path_list2[i])):
            file_path = file_path_list2[i][k]
            data = pd.read_excel(file_path, sheet_name='Sheet1')
            gasUsed = data['gasUsed'].tolist()
            AccGas.append(np.mean(gasUsed))
        Q_Gas.append(AccGas)

    print(Q_Gas)
    '''
    resultData = {'Resource_Number':[500, 1000, 1500, 2000, 2500],'FBSI_Normal':E_Gas[0], 'FBSI_Uniform':E_Gas[1],
                'Quad_Normal':Q_Gas[0], 'Quad_Uniform':Q_Gas[1]}
    file_path = r'C:\WorkFile\3-实验室课题研究\研究-NFT辅助资源共享的无人机网络上的可验证查询\小论文扩展\实验数据\查询平均GasCost分析.xlsx'
    pd.DataFrame(resultData).to_excel(file_path, index=False)'''

    data_x = [500, 1000, 1500, 2000, 2500]

    # 折线图
    '''
    ax1.plot(data_x, E_Gas[0],lw=1.5)
    ax1.plot(data_x, Q_Gas[0],lw=1.5)
    ax1.legend(legend, prop=font2) # loc='lower right',
    # 用科学计数法表示坐标轴
    # style='sci' 指明用科学记数法，scilimits=(-1,2) 表示对（10^-1,10^2）范围之外的值换科学记数法，范围内的数不换
    ax1.ticklabel_format(style='sci', scilimits=(1,2), axis='both')
    ax1.set_ylim(170000,500000)

    ax2.plot(data_x, E_Gas[1],lw=1.5)
    ax2.plot(data_x, Q_Gas[1],lw=1.5)
    ax2.legend(legend, prop=font2)# loc='lower right', 
    ax2.ticklabel_format(style='sci', scilimits=(1,2), axis='both')
    ax2.set_ylim(170000,500000)'''

    
    # 柱状图
    x = np.arange(5)  # x轴刻度标签位置
    width = 0.4  # 柱子的宽度
    ''''''
    # 计算每个柱子在x轴上的位置，保证x轴刻度标签居中
    ax1.bar(x - 0.5 * width, E_Gas[0], width, color=color[0], edgecolor='k', hatch='xx', alpha=1)
    ax1.bar(x + 0.5 * width, Q_Gas[0], width, color=color[1], edgecolor='k', hatch='/', alpha=1)
    ax1.set_ylim(0, 460000)
    ax1.set_xticks(x, labels=data_x, size=frontsize)
    ax1.legend(legend, loc='upper left', prop=font2)

    # 用科学计数法表示坐标轴，e为底
    # style='sci' 指明用科学记数法，scilimits=(-1,2) 表示对（10^-1,10^2）范围之外的值换科学记数法，范围内的数不换
    # ax1.ticklabel_format(style='sci', scilimits=(1,2), axis='y')
    # 10为底
    formatter = ticker.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((0,0))
    ax1.yaxis.set_major_formatter(formatter)

    
    ax2.bar(x - 0.5 * width, E_Gas[1], width, color=color[0], edgecolor='k', hatch='xx', alpha=1)
    ax2.bar(x + 0.5 * width, Q_Gas[1], width, color=color[1], edgecolor='k', hatch='/', alpha=1)
    ax2.set_ylim(0, 460000)
    ax2.set_xticks(x, labels=data_x, size=frontsize)
    ax2.legend(legend, loc='upper left', prop=font2)
    ax2.yaxis.set_major_formatter(formatter)
    
    plt.rc('font', size=18)
    plt.show()

# 计算一个excel中sheet1中"gasUsed"和"time_end"-"time_start"的平均值
def meanOfGasAndTime(file):
    data = pd.read_excel(file, sheet_name='Sheet1')
    average_gas = np.mean(data['gasUsed'].tolist())
    average_time = np.mean((data['time_end']-data['time_start']).tolist())
    return average_gas, average_time

# 分批注入2500个资源数据，每500个时执行范围比查询（0.1%-0.6%，每组50个），统计平均查询时间和gas cost
def TimeAndGasForRangePercentageQuery(file_path_list1, result_file_path):
    # 从磁盘读取结果存放文件    
    resultData = pd.read_excel(result_file_path, sheet_name='Sheet1')
    
    # 处理第一组文件
    for i in range(0,len(file_path_list1)):
        result = meanOfGasAndTime(file_path_list1[i])
        resultData.loc[int(i/6),'{}_gas'.format(i%6/10)] = int(result[0]) # 取整数部分
        resultData.loc[int(i/6),'{}_time'.format(i%6/10)] = round(result[1],3) # 保留小数点后3位，去掉多余的0

    pd.DataFrame(resultData).to_excel(result_file_path, index=False)

# 计算资源在FBSI和quad上的存储深度分布，结果打印输出，需手动存储到excel中
def DepthOfData(file_path, column1, column2):
    # 从磁盘读取结果存放文件    
    data = pd.read_excel(file_path, sheet_name='Sheet1')

    Count = data[column1].tolist()
    Layer = data[column2].tolist()
    # 去掉结果为Null的数据
    for i in range(1, len(Count)):
        if data.loc[i,column1] != data.loc[i,column1]:
            Count = Count[0:i]
            Layer = Layer[0:i]
            break

    # 计算每层的data比列
    sumCount = sum(Count)
    scores = {}
    for i in range(1, len(Count)):
        if Layer[i] in scores:
            scores[Layer[i]] += Count[i]
        else:
            scores[Layer[i]] = Count[i]
    for item in scores:
        scores[item] = scores[item]/sumCount
    print(scores)

# 绘制资源在FBSI和quad上的存储深度分布
def drawDepthOfData(file_path):
    # 从磁盘读取结果存放文件    
    data = pd.read_excel(file_path, sheet_name='Sheet2')

    depth = data['depth'].tolist()
    NormalFBSI = data['NormalFBSI'].tolist()
    NormalQuad = data['NormalQuad'].tolist()
    UniformFBSI = data['UniformFBSI'].tolist()
    UniformQuad = data['UniformQuad'].tolist()

    # 创建画板 
    frontsize = 20
    font2 = {'size': 16}
    legend = ['Proposed FBSI', 'Quad-Tree']
    legend1 = ['Proposed FBSI-Normal', 'Quad-Tree-Normal','Proposed FBSI-Uniform', 'Quad-Tree-Uniform']
    color = [(98 / 255, 159 / 255, 202 / 255), (255 / 255, 229 / 255, 206 / 255)]
    # 创建画板1，显示正态分布的数据深度分布
    fig1 = plt.figure(1)  # 如果不传入参数默认画板1
    ax1 = fig1.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.15, right=0.99, top=0.96, bottom=0.15)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    ax1.set_xlabel('Depth (Normal)', size=frontsize)
    ax1.set_ylabel('Data proportion (%)', size=frontsize)
    # 创建画板2，显示均匀分布的数据深度分布
    fig2 = plt.figure(2)
    ax2 = fig2.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.15, right=0.99, top=0.96, bottom=0.15)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    ax2.set_xlabel('Depth (Uniform)', size=frontsize)
    ax2.set_ylabel('Data proportion (%)', size=frontsize)

    # 折线图
    ''''''
    ax1.plot(depth[2:6], NormalFBSI[2:6],lw=1.5, marker = 'o')
    ax1.plot(depth[2:11], NormalQuad[2:11],lw=1.5, marker = '*')
    ax1.plot(depth[2:6], UniformFBSI[2:6],lw=1.5, linestyle='--', marker = 'o')
    ax1.plot(depth[3:7], UniformQuad[3:7],lw=1.5, linestyle='--', marker = '*')
    ax1.legend(legend1, prop=font2) # loc='lower right',
    ax1.set_xlim(1.5, 10.5)
    ax1.set_ylim(0,100)

    ax2.plot(depth[2:6], UniformFBSI[2:6],lw=1.5, marker = 'o')
    ax2.plot(depth[3:7], UniformQuad[3:7],lw=1.5, marker = '*')
    ax2.legend(legend, prop=font2)
    ax2.set_xlim(1.5, 10.5)
    ax2.set_ylim(0,80)
    # ax2.annotate('1e5', xy =(3,3), xytext=(9, -10), size=frontsize,arrowprops=dict(facecolor='black', shrink=0.01))
    # 添加注释 参数名xy：箭头注释中箭头所在位置，参数名xytext：注释文本所在位置，
    #arrowprops在xy和xytext之间绘制箭头, shrink表示注释点与注释文本之间的图标距离

    plt.show()


# 给出3组x，y数组，绘制折线图
def drawLineFig():
    '''
    # 订阅查询-均匀分布-gas开销
    x1 = [20,40,60,80,100,150, 200, 250, 300, 350, 400, 450, 500]
    y1 = [138704.25,140295.2,151441.15,143902.6,126217.45,133203.38,
          129122.64,127119.72,137401.9,134665.82,136533.88,135065.54,126712.1]
    x2 = [20,40,60,80,100]
    y2 = [158011,146418.1579,157234.7778,154281.7895,162377]
    x3 = [20,40,60,80,100]
    y3 = [249018.2,414831.4,580622.6,746294.6,912376.2]
    
    # 订阅查询-正态分布-gas开销
    x1 = [20,40,60,80,100,150, 200, 250, 300, 350, 400, 450, 500]
    y1 = [133976.2,140359.35,128994.1,134606.5,139794.82,131452.24,
          127028.36,135458.42,133225.04,131950.06,127222.24,130092.94,134688.32]
    x2 = [20,40,60]
    y2 = [140070.2,148548.35,180810.2]
    x3 = [20,40,60,80,100]
    y3 = [249017,414835.6,580675.4,746457.8,912197.2105]
     
    # 订阅查询-均匀分布-时间开销
    x1 = [20,40,60,80,100,150, 200, 250, 300, 350, 400, 450, 500]
    y1 = [0.97981744,0.93206528,1.13998658,0.94767115,0.630416055,0.783339062,
          0.673626046,0.659307926,0.886235616,0.755088846,0.799846622,0.770482048,
          0.58283959]
    x2 = [20,40,60,80,100]
    y2 = [1.180952875,1.185316347,1.280769261,1.253338642,1.299531285]
    x3 = [20,40,60,80,100]
    y3 = [2.412626875,4.01594755,5.60186028,8.356290675,9.055255395]
   
    # 订阅查询-正态分布-时间开销
    x1 = [20,40,60,80,100,150, 200, 250, 300, 350, 400, 450, 500]
    y1 = [0.974207705,0.91795397,0.75946116,0.865594205,1.011218194,0.781967176,
          0.686905354,0.810061234,0.78810741,0.738402568,0.622476194,0.708670908,
          0.815863004]
    x2 = [20,40,60]
    y2 = [1.02128571,1.179023705,1.43487622]
    x3 = [20,40,60,80,100]
    y3 = [2.433624465,4.00838282,5.630202235,8.28169647,9.138698716]
    
              
    # 小样本单次查询-均匀分布-gas开销
    x1 = [20,40,60,80,100,120, 140]
    y1 = [225720.7,328754.5,280281.15,268894.35,197311.85,230953.3,196486.95]
    x2 = [20,40,60,80,100,120, 140]
    y2 = [298917.3684,293298.55,240481.65,302493.7,310838.85,391821.45,422525.6]
    x3 = [20,40,60,80,100,120, 140]
    y3 = [855109.5,1551567.7,2378254.25,3177249.05,3657797,4869623.85,5573296.55,]  
          
    # 小样本单次查询-正态分布-gas开销
    x1 = [20,40,60,80,100,120, 140]
    y1 = [358781.8,324387.8,335583.4,245218.25,218586.05,304851.45,206605.2]
    x2 = [20,40,60,80,100,120, 140]
    y2 = [397107.25,341165.7895,275299.35,286119.55,328677.65,308219.35,349068.55]
    x3 = [20,40,60,80,100,120, 140]
    y3 = [798188.4,1473752.85,2200994.2,2696733.7,3528130.5,4244484.85,5302597.5]
    
    # 小样本单次查询-均匀分布-时间开销
    x1 = [20,40,60,80,100,120, 140]
    y1 = [0.37546723,0.497463755,0.46386441,0.55283821,0.343053215,0.384131595,
          0.330022415]
    x2 = [20,40,60,80,100,120, 140]
    y2 = [0.483082995,0.506891835,0.455468445,0.77838348,0.545703505,0.632810095,
          0.665027375]
    x3 = [20,40,60,80,100,120, 140]
    y3 = [1.10774401,1.800884855,2.601476075,3.503968,4.036897665,5.30791342,
          6.009195485]'''
    
    # 小样本单次查询-正态分布-时间开销
    x1 = [20,40,60,80,100,120, 140]
    y1 = [0.528433105,0.507395865,0.54076167,0.419132525,0.373505705,0.499632445,
          0.371665865]
    x2 = [20,40,60,80,100,120, 140]
    y2 = [0.592170225,0.550325016,0.466763965,0.51638935,0.552091725,0.58643012,
          0.56717243]
    x3 = [20,40,60,80,100,120, 140]
    y3 = [0.96301565,1.63050623,2.40174033,2.945732085,3.79377627,4.60118602,
          5.698918145]
    ''' '''
    
    


    # 创建画板
    frontsize = 20
    font2 = {'size': 18}
    fig1 = plt.figure(1)
    ax1 = fig1.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.14, right=0.99, top=0.94, bottom=0.15)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)

    color = [(31 / 255, 120 / 255, 180 / 255), (255 / 255, 127 / 255, 0 / 255), 
             (100 / 255, 100 / 255, 100 / 255)]
    legend = ['Proposed FBSI', 'Quad-Tree', 'Indexless']

    ax1.plot(x1, y1, linewidth=2.5, color=color[0], marker='o')# 圆点
    ax1.plot(x2, y2, linewidth=2.5, color=color[1], marker='o')
    ax1.plot(x3, y3, linewidth=2.5, color=color[2], marker='o')
    ax1.grid(ls='--') #设置虚线网格


    ax1.set_xlabel('数据量（正态分布）', size=frontsize)
    ax1.set_ylabel('平均时间（s）', size=frontsize) # 'Number of Resources'
    ax1.set_ylim(0, 7)
    # y坐标采用科学计数法，以10为底
    formatter = ticker.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((0,0))
    ax1.yaxis.set_major_formatter(formatter)

    ax1.legend(legend, loc='upper left', prop=font2)

    plt.show()


if __name__ == '__main__':
     
    # drawLineFig()

    FBSI_contract_address = '0xd970244279325E673b3FDC62B3b36D6B1CbF09bf'
    Quad_contract_address = '0x8c3A2cCfaa1F2c7125e7FEBacE9638B6c2C0387D'
    FBSI_contract_ABI = 'FBSIQuery.abi'
    Quad_contract_ABI = 'QuadQuery.abi'

    path_prefix = r'C:\WorkFile\5-毕业课题\单次查询实验\修正节点大小后的实验数据'
    path_result = r'{}\Resource_number_on_leaf_node.xlsx'.format(path_prefix)

    clumnNormallyFBSIToken = 'NormallyFBSITokenCount'
    clumnNormallyFBSILayer = 'NormallyFBSILayer'
    clumnUniformFBSIToken = 'UniformFBSITokenCount'
    clumnUniformFBSILayer = 'UniformFBSILayer'
    clumnNormallyQuadToken = 'NormallyQuadTokenCount'
    clumnNormallyQuadLayer = 'NormallyQuadLayer'
    clumnUniformQuadToken = 'UniformQuadTokenCount'
    clumnUniformQuadLayer = 'UniformQuadLayer'
    
    # statisticsResourceNumberOnLeafNode(FBSI_contract_address, FBSI_contract_ABI, path_result, clumnNormallyFBSIToken, clumnNormallyFBSILayer)
    # statisticsResourceNumberOnLeafNode(FBSI_contract_address, FBSI_contract_ABI, path_result, clumnUniformFBSIToken, clumnUniformFBSILayer)
    # statisticsResourceNumberOnLeafNode(Quad_contract_address, Quad_contract_ABI, path_result, clumnNormallyQuadToken, clumnNormallyQuadLayer)
    # statisticsResourceNumberOnLeafNode(Quad_contract_address, Quad_contract_ABI, path_result, clumnUniformQuadToken, clumnUniformQuadLayer)
    
    # drawCalculatedRatioOfLeafNode(path_result)# 叶节点饱和度统计图

    ExperimentData_file_path_list = [r'{}\FBSI-fan7\Normally_FBSIBuild_test.xlsx'.format(path_prefix),
                                     r'{}\Quad\Normally_QuadTreeBuild_test.xlsx'.format(path_prefix),
                                     r'{}\FBSI-fan7\Uniform_FBSIBuild_test.xlsx'.format(path_prefix),
                                     r'{}\Quad\Uniform_quadTreeBuild_test.xlsx'.format(path_prefix)]
    
    # drawBuildResultOfSplitTime(ExperimentData_file_path_list)# 节点分裂时间统计图
    # drawBuildResultOfNodeToData(ExperimentData_file_path_list)# 节点-数据量关系图

    # drawBuildTreeGasCostSplit(ExperimentData_file_path_list)# 插入数据导致节点分裂的gas开销与数据量关系图
    
    # drawBuildTreeGasCostUnsplit(ExperimentData_file_path_list)# 插入数据未导致节点分裂的gas开销与数据量关系图
 
    
    file_path_list1 = [[r'{}\FBSI-fan7\Normally_FBSIQuery_500.xlsx'.format(path_prefix),
                        r'{}\FBSI-fan7\Normally_FBSIQuery_1000.xlsx'.format(path_prefix),
                        r'{}\FBSI-fan7\Normally_FBSIQuery_1500.xlsx'.format(path_prefix),
                        r'{}\FBSI-fan7\Normally_FBSIQuery_2000.xlsx'.format(path_prefix),
                        r'{}\FBSI-fan7\Normally_FBSIQuery_2500.xlsx'.format(path_prefix)],

                       [r'{}\FBSI-fan7\Uniform_FBSIQuery_500.xlsx'.format(path_prefix),
                        r'{}\FBSI-fan7\Uniform_FBSIQuery_1000.xlsx'.format(path_prefix),
                        r'{}\FBSI-fan7\Uniform_FBSIQuery_1500.xlsx'.format(path_prefix),
                        r'{}\FBSI-fan7\Uniform_FBSIQuery_2000.xlsx'.format(path_prefix),
                        r'{}\FBSI-fan7\Uniform_FBSIQuery_2500.xlsx'.format(path_prefix)]]
    

    file_path_list2 = [[r'{}\Quad\Normally_QuadTreeQuery_500.xlsx'.format(path_prefix),
                        r'{}\Quad\Normally_QuadTreeQuery_1000.xlsx'.format(path_prefix),
                        r'{}\Quad\Normally_QuadTreeQuery_1500.xlsx'.format(path_prefix),
                        r'{}\Quad\Normally_QuadTreeQuery_2000.xlsx'.format(path_prefix),
                        r'{}\Quad\Normally_QuadTreeQuery_2500.xlsx'.format(path_prefix)],

                       [r'{}\Quad\Uniform_QuadTreeQuery_500.xlsx'.format(path_prefix),
                        r'{}\Quad\Uniform_QuadTreeQuery_1000.xlsx'.format(path_prefix),
                        r'{}\Quad\Uniform_QuadTreeQuery_1500.xlsx'.format(path_prefix),
                        r'{}\Quad\Uniform_QuadTreeQuery_2000.xlsx'.format(path_prefix),
                        r'{}\Quad\Uniform_QuadTreeQuery_2500.xlsx'.format(path_prefix)]]
    
    
    # drawQueryTimeMaxMinMean(file_path_list1, file_path_list2)# 单次查询的时间开销与数据量关系图
    # drawQueryMaxMinMeanGasCost(file_path_list1, file_path_list2)# 单次查询的的gas开销与数据量关系图
