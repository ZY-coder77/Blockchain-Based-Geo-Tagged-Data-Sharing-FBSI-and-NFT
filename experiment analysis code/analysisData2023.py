import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import seaborn as sns
from web3 import Web3
import json
import os

# path_prefix = r'C:\WorkFile\3-实验室课题研究\研究-NFT辅助资源共享的无人机网络上的可验证查询\实验数据'
path_prefix = r'C:\WorkFile\3-实验室课题研究\研究-NFT辅助资源共享的无人机网络上的可验证查询\小论文扩展\实验数据'

# 通过合约获取每个叶节点上的资源数量，保存在excle文件中
def statisticsResourceNumberOnLeafNode(contractAddress, contractABI, file_path_result, clumnNameCount, clumnNameLayer):
    # 连接Ganache:
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
    # print(w3.isConnected())

    # 获取最新区块号（区块高度）
    print('blockNumber is: %d' % w3.eth.blockNumber)
    ''''''
    # IE-tree结构，扇出为7，单节点最大记录数为5，合约无倒排文件辅助查询
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
def drawCalculatedRatioOfLeafNodeUseSns(file_path):

    fig1 = plt.figure(1)
    ax1 = fig1.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.13, right=0.99, top=0.99, bottom=0.15)
    fig2 = plt.figure(2)
    ax2 = fig2.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.13, right=0.99, top=0.99, bottom=0.15)

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
    ax1.set_xlabel('Data Capacity Ratio (%) (Normal)', font1)
    ax1.set_ylabel('Proportion of Leaf Nodes (%)', font1)
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
    ax2.set_xlabel('Data Capacity Ratio (%) (Uniform)', font1)
    ax2.set_ylabel('Proportion of Leaf Nodes (%)', font1)
    ax2.set_xticks(np.linspace(0.5, 10.5, 11), range(0, 110, 10), size=frontsize)
    ax2.set_yticks(np.linspace(0, 0.25, 6), range(0, 26, 5), size=frontsize)
    ax2.set_xlim(-0.5, 11.5)
    ax2.set_ylim(0, 0.29)
    plt.show()


# 使用seaborn库绘制构建树形结构中节点分裂时间直方图（含概率密度分布曲线）和节点-资源数关系图----y坐标标记点分配未完成
def drawBuildResultUseSns(file_path_list):
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
    plt.subplots_adjust(left=0.14, right=0.96, top=0.99, bottom=0.16)
    
    fig2 = plt.figure(2)
    ax2 = fig2.add_subplot(1, 1, 1)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    plt.subplots_adjust(left=0.14, right=0.96, top=0.99, bottom=0.16)
    
    
    subplot = [ax1, ax2]

    fig3 = plt.figure(3)
    ax3 = fig3.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.14, right=0.96, top=0.95, bottom=0.15)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    
    fig4 = plt.figure(4)
    ax4 = fig4.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.14, right=0.96, top=0.95, bottom=0.15)
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


    # fig1.subplots_adjust(hspace=0.5)
    ax1.set_xlabel('Time for Splitting a Node (s)(Normal)', size=frontsize)
    ax1.set_ylabel('Proportion of Split Nodes (%)', size=frontsize)
    ax1.set_xlim(0.5, 5.0)
    ax1.set_yticks(np.linspace(0, 1.2, 8), range(0, 36, 5))
    ax1.set_ylim(0.0, 1.3)
    # ax1.legend(legend, loc='upper right', prop=font1)

    ax2.set_xlabel('Time for Splitting a Node (s)(Uniform)', size=frontsize)
    ax2.set_ylabel('Proportion of Split Nodes (%)', size=frontsize)
    ax2.set_xlim(0.5, 5.0)
    ax2.set_yticks(np.linspace(0, 1.2, 8), range(0, 36, 5))
    ax2.set_ylim(0.0, 1.3)
    # ax2.legend(legend, loc='upper right', prop=font1)

    ax3.fill_between(node_count_list[0], tokenID_list[0], 0,  # 上限，下限
                     facecolor=colorlist[3],  # 填充颜色
                     alpha=0.2)  # 透明度
    ax3.fill_between(node_count_list[1], tokenID_list[1], 0,  # 上限，下限
                     facecolor=colorlist[2],  # 填充颜色
                     alpha=0.2)  # 透明度
    ax3.set_xlabel('Number of Nodes (Normal)', size=frontsize)
    ax3.set_ylabel('NFT Objects', size=frontsize) # 'Number of Resources'
    ax3.set_xlim(0, 520)
    ax3.set_ylim(0, 2700)
    ax3.ticklabel_format(style='sci', scilimits=(1,2), axis='y')

    ax3.legend(legend, prop=font1)
    print('数据容量-normal-FBSI：', tokenID_list[0][len(tokenID_list[0])-1])
    print('数据容量-normal-quad：', tokenID_list[1][len(tokenID_list[1]) - 1])

    ax4.fill_between(node_count_list[2], tokenID_list[2], 0,  # 上限，下限
                     facecolor=colorlist[3],  # 填充颜色
                     alpha=0.2)  # 透明度
    ax4.fill_between(node_count_list[3], tokenID_list[3], 0,  # 上限，下限
                     facecolor=colorlist[2],  # 填充颜色
                     alpha=0.2)  # 透明度
    ax4.set_xlabel('Number of Nodes (Uniform)', size=frontsize)
    ax4.set_ylabel('NFT Objects', size=frontsize)# 'Number of Resources'
    ax4.set_xlim(0, 520)
    ax4.set_ylim(0, 2700)
    ax4.ticklabel_format(style='sci', scilimits=(1,2), axis='y')

    ax4.legend(legend, prop=font1)
    print('数据容量-uniform-FBSI：', tokenID_list[2][len(tokenID_list[2]) - 1])
    print('数据容量-uniform-quad：', tokenID_list[3][len(tokenID_list[3]) - 1])

    # 显示图像
    plt.show()

# 分析节点分裂的gas cost，和未发生节点分裂时的插入数据gas cost与资源数量的关系
def drawBuildTreeGasCost(file_path_list):
    '''
    startnum = 0
    endnum = 2500
    file_path = file_path_list[3]
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    tokenID = data['tokenID'][startnum:endnum].tolist()
    gasUsed = data['gasUsed'][startnum:endnum].tolist()
    node_count = data['node_count'][startnum:endnum].tolist()

    # 分裂分裂点的gasUsed和tokenID和的非分裂gasUsed和tokeID
    gasUsedSplit = []
    tokenIDSplit = []
    gasUsedUnSplit = []
    tokenIDUnSplit = []
    gasUsedUnSplit.append(gasUsed[0])
    tokenIDUnSplit.append(tokenID[0])
    j = 1
    while j<len(tokenID):
        if node_count[j-1]<node_count[j]:
            gasUsedSplit.append(gasUsed[j])
            tokenIDSplit.append(tokenID[j])
        else:
            gasUsedUnSplit.append(gasUsed[j])
            tokenIDUnSplit.append(tokenID[j])
        j += 1
    resultData = {'tokenIDUnSplit':tokenIDUnSplit, 'gasUsedUnSplit':gasUsedUnSplit}
    file_path = r'C:\WorkFile\3-实验室课题研究\研究-NFT辅助资源共享的无人机网络上的可验证查询\小论文扩展\实验数据\插入数据GasCost分析.xlsx'
    pd.DataFrame(resultData).to_excel(file_path, index=False)'''
    
    startnum = 0
    endnum = 2500

    # 创建画板
    frontsize = 20
    frontsize2 = 17
    fig1 = plt.figure(1)
    ax1 = fig1.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.14, right=0.96, top=0.95, bottom=0.16)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    fig2 = plt.figure(2)
    ax2 = fig2.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.14, right=0.96, top=0.95, bottom=0.16)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    subplot = [ax1, ax2]

    fig3 = plt.figure(3)
    ax3 = fig3.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.18, right=0.96, top=0.95, bottom=0.15)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    fig4 = plt.figure(4)
    ax4 = fig4.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.18, right=0.96, top=0.95, bottom=0.15)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    subplot2 = [ax3, ax4]

    font1 = {'size': 18}
    legend = ['Proposed FBSI', 'Proposed FBSI', 'Quad-Tree', 'Quad-Tree']
    alpha = [0.7, 0.2]

    for i in range(0, len(file_path_list)):
        file_path = file_path_list[i]
        data = pd.read_excel(file_path, sheet_name='Sheet1')
        tokenID = data['tokenID'][startnum:endnum].tolist()
        gasUsed = data['gasUsed'][startnum:endnum].tolist()
        node_count = data['node_count'][startnum:endnum].tolist()

        # 分裂分裂点的gasUsed和tokenID和的非分裂gasUsed和tokeID
        gasUsedSplit = []
        tokenIDSplit = []
        gasUsedUnSplit = []
        tokenIDUnSplit = []
        gasUsedUnSplit.append(gasUsed[0])
        tokenIDUnSplit.append(tokenID[0])
        j = 1
        while j<len(tokenID):
            if node_count[j-1]<node_count[j]:
                gasUsedSplit.append(gasUsed[j])
                tokenIDSplit.append(tokenID[j])
            else:
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
        subplot[int(i/2)].plot(tokenIDSplit,gasUsedSplit,lw=1.5)
        subplot2[int(i/2)].plot(sparse_tokenIDUnSplit,sparse_gasUsedUnSplit,lw=1)
        # 绘制gasUsed统计直方图，前两个Excel数据绘制在同一幅，后两个绘制在同一幅 binrange=(0.5, 5.0), 
        # sns.histplot(gasUsedSplit, bins=25, binrange=(0, 3500000), stat='percent', kde=False, alpha=alpha[int(i%2)], ax=subplot[int(i/2)])
        # sns.histplot(gasUsedUnSplit, bins=25, binrange=(220000, 400000), stat='percent', kde=False, alpha=alpha[int(i%2)], ax=subplot2[int(i/2)])
        # 绘制gasUsed拟合曲线，前两个Excel数据绘制在同一幅，后两个绘制在同一幅
        # sns.kdeplot(gasUsedSplit, linewidth=2.5, ax=subplot[int(i/2)])
        # sns.kdeplot(gasUsedUnSplit, linewidth=2.5, ax=subplot2[int(i/2)])

        print('分裂点数量: ', len(gasUsedSplit))
        print('非分裂点数量: ', len(gasUsedUnSplit))
    
    '''折线图的坐标轴设置'''
    legend = ['Proposed FBSI', 'Quad-Tree']
    # ax1.set_title('Gas Cost of Inserting Data with Node Spliting (Normal)')
    ax1.set_xlabel('Database Size (Normal)', size=frontsize)
    ax1.set_ylabel('Gas Cost of Inserting Data (Split)', size=frontsize2)
    ax1.legend(legend, loc='upper right', prop=font1)
    ax1.set_yticks(range(0, 3600000, 500000))
    ax1.ticklabel_format(style='sci', scilimits=(1,2), axis='both')
    ax1.set_ylim(400000,3600000)

    # ax2.set_title('Gas Cost of Inserting Data with Node Spliting (Uniform)')
    ax2.set_xlabel('Database Size (Uniform)', size=frontsize)
    ax2.set_ylabel('Gas Cost of Inserting Data (Split)', size=frontsize2)
    ax2.legend(legend, loc='upper right', prop=font1)
    ax2.set_yticks(range(0, 3100000, 500000))
    ax2.ticklabel_format(style='sci', scilimits=(1,2), axis='both')
    ax2.set_ylim(400000,3100000)
    
    # ax3.set_title('Gas Cost of Inserting Data with Node Non-Spliting (Normal)')
    ax3.set_xlabel('Database Size (Normal)', size=frontsize)
    ax3.set_ylabel('Gas Cost of Inserting Data (Unsplit)', size=frontsize2)
    ax3.legend(legend, loc='lower right', prop=font1)
    ax3.ticklabel_format(style='sci', scilimits=(1,2), axis='both')
    ax3.set_ylim(216000,385000)

    # ax4.set_title('Gas Cost of Inserting Data with Node Non-Spliting (Uniform)')
    ax4.set_xlabel('Database Size (Uniform)', size=frontsize)
    ax4.set_ylabel('Gas Cost of Inserting Data (Unsplit)', size=frontsize2)
    ax4.legend(legend, loc='lower right', prop=font1)
    ax4.ticklabel_format(style='sci', scilimits=(0,0), axis='both')
    ax4.set_ylim(216000,385000)

    '''直方图的坐标轴设置
    ax1.set_xlabel('Gas Cost of Inserting Data (Node Spliting) (Normal)', size=frontsize)
    ax1.set_ylabel('Proportion of Split Nodes (%)', size=frontsize)
    ax1.legend(legend, loc='upper right', prop=font1)
    ax1.ticklabel_format(style='sci', scilimits=(0,0), axis='both')

    ax2.set_xlabel('Gas Cost of Inserting Data (Node Spliting) (Uniform)', size=frontsize)
    ax2.set_ylabel('Proportion of Split Nodes (%)', size=frontsize)
    ax2.legend(legend, loc='upper right', prop=font1)
    ax2.ticklabel_format(style='sci', scilimits=(0,0), axis='both')
    
    ax3.set_xlabel('Gas Cost of Inserting Data (No Node Spliting) (Normal)', size=frontsize)
    ax3.set_ylabel('Proportion of Data (%)', size=frontsize)
    ax3.legend(legend, loc='lower right', prop=font1)
    ax3.ticklabel_format(style='sci', scilimits=(0,0), axis='x')

    ax4.set_xlabel('Gas Cost of Inserting Data (No Node Spliting) (Uniform)', size=frontsize)
    ax4.set_ylabel('Proportion of Data (%)', size=frontsize)
    ax4.legend(legend, loc='lower right', prop=font1)
    ax4.ticklabel_format(style='sci', scilimits=(0,0), axis='x')
    '''

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
    plt.subplots_adjust(left=0.15, right=0.99, top=0.96, bottom=0.15)
    plt.yticks(fontsize=frontsize)
    ax1.set_xlabel('Number of blocks (Normal)', size=frontsize)
    ax1.set_ylabel('Average CPU Time (s)', size=frontsize)

    fig2 = plt.figure(2)
    ax2 = fig2.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.15, right=0.99, top=0.96, bottom=0.15)
    plt.yticks(fontsize=frontsize)
    ax2.set_xlabel('Number of blocks (Uniform)', size=frontsize)
    ax2.set_ylabel('Average CPU Time (s)', size=frontsize)

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
    plt.subplots_adjust(left=0.15, right=0.99, top=0.96, bottom=0.15)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    ax1.set_xlabel('Database Size (Normal)', size=frontsize)
    ax1.set_ylabel('Average Gas Cost', size=frontsize)

    fig2 = plt.figure(2)
    ax2 = fig2.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.15, right=0.99, top=0.96, bottom=0.15)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    ax2.set_xlabel('Database Size (Uniform)', size=frontsize)
    ax2.set_ylabel('Average Gas Cost', size=frontsize)

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
    # 用科学计数法表示坐标轴
    # style='sci' 指明用科学记数法，scilimits=(-1,2) 表示对（10^-1,10^2）范围之外的值换科学记数法，范围内的数不换
    ax1.ticklabel_format(style='sci', scilimits=(1,2), axis='y')
    
    ax2.bar(x - 0.5 * width, E_Gas[1], width, color=color[0], edgecolor='k', hatch='xx', alpha=1)
    ax2.bar(x + 0.5 * width, Q_Gas[1], width, color=color[1], edgecolor='k', hatch='/', alpha=1)
    ax2.set_ylim(0, 460000)
    ax2.set_xticks(x, labels=data_x, size=frontsize)
    ax2.legend(legend, loc='upper left', prop=font2)
    ax2.ticklabel_format(style='sci', scilimits=(1,2), axis='y')
     

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

# 使用seaborn库绘制查询树构建时节点分裂时间直方图（含概率密度分布曲线）和节点资源关系图
def drawBuildQueryTreeResult():
    startnum = 0
    endnum = 100
    node_capacity = 5
    colorlist = [(214 / 255, 39 / 255, 40 / 255), (44 / 255, 160 / 255, 44 / 255),
                 (31 / 255, 119 / 255, 180 / 255), (255 / 255, 127 / 255, 14 / 255), 'k', 'tan', 'darkorange',
                 'aquamarine', 'm', 'navy']
    markerlist = ['3', '3', '4', '4', '.', '.', '+', '+', 'x', 'x']
    file_path_list = [r'C:\WorkFile\服务器实验数据\订阅查询实验\Normally_IETreeBuild_Subscription.xlsx',
                      r'C:\WorkFile\服务器实验数据\订阅查询实验\Uniform_IETreeBuild_Subscription.xlsx',
                      r'C:\WorkFile\服务器实验数据\订阅查询实验\Uniform_QuadTreeBuild_Subscription.xlsx']
    # 创建画板1，显示正态分布的构建时间
    # 如果不传入参数默认画板1
    fig2 = plt.figure(2)
    fig3 = plt.figure(3)
    legend = ['Proposed E-tree Normal', 'Proposed E-tree Uniform', 'Quad-tree Uniform']
    # 第2步创建画纸，并选择画纸1
    ax5 = fig2.add_subplot(1, 1, 1)
    ax6 = fig3.add_subplot(1, 1, 1)
    frontsize = 12
    hatchlist = ['xx', '//', '\\\\']
    queryID_list = []
    node_count_list = []
    for i in range(0, len(file_path_list)):
        file_path = file_path_list[i]
        data = pd.read_excel(file_path, sheet_name='Sheet1')
        queryID = data['queryID'][startnum:endnum]
        time_start = data['time_start'][startnum:endnum]
        time_end = data['time_end'][startnum:endnum]
        node_count = data['node_count'][startnum:endnum]

        temptime = time_end - time_start
        accumulative_time = time_end - time_start
        # 过滤time中小于0.5秒的数据，主要观察其中的分裂时间
        temptime = temptime.tolist()
        time = []
        for k in range(0, len(temptime)):
            if temptime[k] >= 4.5:
                time.append(temptime[k])

        for j in range(1, len(accumulative_time)):
            accumulative_time[j] += accumulative_time[j - 1]
        '''
        subplot[i].hist(x=time, bins=20, range=(4.5, 10), weights=[1./len(time)]*len(time), color='steelblue', edgecolor='black',
                        rwidth= 0.5)
        subplot[i].set_xlabel('Time for Splitting a Node (s)', size=frontsize)
        subplot[i].set_ylabel('Proportion of Split Nodes', size=frontsize)
        subplot[i].set_ylim(0,0.25)
        subplot[i].set_xlim(4.5,10)
        subplot[i].text(6.5,0.22,legend[i],fontsize=12,color='k')
        ax5.plot(queryID, node_count, color=colorlist[i])'''

        sns.histplot(time, bins=30, binrange=(4.5, 10.0), stat='density', kde=False, hatch=hatchlist[i], alpha=0.2,
                     ax=ax5)
        sns.kdeplot(time, ax=ax5)
        ax5.lines[-1].set_linestyle('--')  # stat='density'   stat='percent'  line_kws={'linestyle': '--'}
        # 删除资源数量增加但节点不增的数据
        queryID = queryID.tolist()
        node_count = node_count.tolist()
        j = 1
        while j < len(queryID):
            if node_count[j] > 33:
                queryID.pop(j)
                node_count.pop(j)
                continue
            if node_count[j - 1] == node_count[j]:
                queryID.pop(j - 1)
                node_count.pop(j - 1)
            else:
                j += 1
        queryID_list.append(queryID)
        node_count_list.append(node_count)
        print(node_count[len(node_count) - 1])

        # 绘制节点数据-资源数量关系图
        ax6.plot(node_count, queryID, color=colorlist[i], alpha=0.8)

    ax5.set_xlabel('Time for Splitting a Node (s)', size=frontsize)
    ax5.set_ylabel('Proportion of Split Nodes (%)', size=frontsize)
    ax5.set_yticks(np.linspace(0, 1.36489, 6), range(0, 26, 5))
    ax5.set_xlim(4, 10)
    ax5.set_ylim(0, 1.22)
    ax5.legend(legend)

    ax6.fill_between(node_count_list[0], queryID_list[0], 0,  # 上限，下限
                     facecolor=colorlist[0],  # 填充颜色
                     alpha=0.2)  # 透明度
    ax6.fill_between(node_count_list[1], queryID_list[1], 0,  # 上限，下限
                     facecolor=colorlist[1],  # 填充颜色
                     alpha=0.2)  # 透明度
    ax6.fill_between(node_count_list[2], queryID_list[2], 0,  # 上限，下限
                     facecolor=colorlist[2],  # 填充颜色
                     alpha=0.2)  # 透明度
    ax6.set_xlabel('Number of Nodes', size=frontsize)
    ax6.set_ylabel('Number of Subscription Queries', size=frontsize)
    ax6.legend(legend)
    # 显示图像
    plt.show()


def drawSubscriptionQueryTime():
    colorlist = ['r', 'g', 'b', 'y', 'k', 'tan', 'darkorange', 'aquamarine', 'm', 'navy']
    markerlist = ['3', '3', '4', '4', '.', '.', '+', '+', 'x', 'x']
    legend1 = ['IE-tree normal', 'IE-tree uniform', 'Quad-tree normal', 'Quad-tree uniform']
    legend2 = ['IE-tree normal', 'IE-tree uniform', 'Quad-tree uniform']

    file_path_list1 = [r'C:\WorkFile\服务器实验数据\二分法查询实验（500）\Normally_IETreeQuery_500_Min_fan7.xlsx',
                       r'C:\WorkFile\服务器实验数据\二分法查询实验（500）\Uniform_IETreeQuery_500_Min_fan7.xlsx',
                       r'C:\WorkFile\服务器实验数据\二分法查询实验（500）\Normally_QuadTreeQuery_500.xlsx',
                       r'C:\WorkFile\服务器实验数据\二分法查询实验（500）\Uniform_QuadTreeQuery_500.xlsx']

    file_path_list1 = [r'C:\WorkFile\服务器实验数据\订阅查询实验\Normally_IETree_Subscription_stream0-3000.xlsx',
                       r'C:\WorkFile\服务器实验数据\订阅查询实验\Uniform_IETree_Subscription_stream0-3000.xlsx',
                       r'C:\WorkFile\服务器实验数据\订阅查询实验\Uniform_QuadTree_Subscription_stream0-3000.xlsx']

    for i in range(0, len(file_path_list1)):
        file_path = file_path_list1[i]
        data = pd.read_excel(file_path, sheet_name='Sheet1')
        # queryNo = data['queryNo']
        queryNo = data['tokenID']
        time_start = data['time_start']
        time_end = data['time_end']
        # 处理时间数据
        accumulative_time = time_end - time_start
        for j in range(1, len(accumulative_time)):
            accumulative_time[j] += accumulative_time[j - 1]
        plt.plot(queryNo, accumulative_time, color=colorlist[i])

    plt.legend(legend2)
    plt.xlabel('Query Sequence')
    plt.ylabel('Accumulative Query CPU Time (s)')
    plt.show()



if __name__ == '__main__':
    
    FBSI_contract_address = '0xd970244279325E673b3FDC62B3b36D6B1CbF09bf'
    Quad_contract_address = '0x8c3A2cCfaa1F2c7125e7FEBacE9638B6c2C0387D'
    FBSI_contract_ABI = 'FBSIQuery.abi'
    Quad_contract_ABI = 'QuadQuery.abi'

    path_prefix = r'C:\WorkFile\3-实验室课题研究\研究-NFT辅助资源共享的无人机网络上的可验证查询\小论文扩展\实验数据\修正节点大小后的实验数据'
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
    
    drawCalculatedRatioOfLeafNodeUseSns(path_result)

    
    ExperimentData_file_path_list = [r'{}\FBSI-fan7\Normally_FBSIBuild_test.xlsx'.format(path_prefix),
                                     r'{}\Quad\Normally_QuadTreeBuild_test.xlsx'.format(path_prefix),
                                     r'{}\FBSI-fan7\Uniform_FBSIBuild_test.xlsx'.format(path_prefix),
                                     r'{}\Quad\Uniform_quadTreeBuild_test.xlsx'.format(path_prefix)]
    
    # drawBuildResultUseSns(ExperimentData_file_path_list)
    # drawBuildTreeGasCost(ExperimentData_file_path_list)
 
    # path_prefix = r'C:\WorkFile\3-实验室课题研究\研究-NFT辅助资源共享的无人机网络上的可验证查询\小论文扩展\实验数据'
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
    
    
    # drawQueryTimeMaxMinMean(file_path_list1, file_path_list2)
    # drawQueryMaxMinMeanGasCost(file_path_list1, file_path_list2)

    path_prefix = r'C:\WorkFile\3-实验室课题研究\研究-NFT辅助资源共享的无人机网络上的可验证查询\小论文扩展\实验数据\修正节点大小后的实验数据\范围比查询结果(经度划分)'
    file_path_list1 = [r'{}\Uniform_QuadTreeQuery_2500_0.01.xlsx'.format(path_prefix),
                        r'{}\Uniform_QuadTreeQuery_2500_0.02.xlsx'.format(path_prefix)]

    path_prefix = r'C:\WorkFile\3-实验室课题研究\研究-NFT辅助资源共享的无人机网络上的可验证查询\小论文扩展\实验数据\修正节点大小后的实验数据'
    result_file = r'{}\范围比查询分析.xlsx'.format(path_prefix)

    # TimeAndGasForRangePercentageQuery(file_path_list1, result_file)

    file_path = r'{}\Resource_number_on_leaf_node.xlsx'.format(path_prefix)
    # DepthOfData(file_path, 'UniformQuadTokenCount', 'UniformQuadLayer')
    # drawDepthOfData(file_path)


    
    # drawBuildQueryTreeResult()

    # drawSubscriptionQueryTime()

