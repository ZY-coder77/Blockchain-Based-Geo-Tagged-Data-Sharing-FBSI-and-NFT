import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import seaborn as sns
from web3 import Web3
import json
import contract5_abi  # IE-tree结构，单次查询，最大扇出数为7，单节点最大记录数为5，合约无倒排文件辅助查询
import contract6_abi  # quad-tree结构，单次查询，单节点最大记录数为5，合约无倒排文件辅助查询

# 通过合约获取每个叶节点上的资源数量，保存在excle文件中
def statisticsResourceNumberOnLeafNode():
    # 连接Ganache:
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
    # print(w3.isConnected())

    # 获取最新区块号（区块高度）
    print('blockNumber is: %d' % w3.eth.blockNumber)
    ''''''
    # IE-tree结构，扇出为7，单节点最大记录数为5，合约无倒排文件辅助查询
    CAKE_BSC_ADDRESS = Web3.toChecksumAddress('0xBA0D5627Bc4C694A67dC9016b70B49f49dcd79E0')
    CAKE_BSC_ABI = json.loads(contract5_abi.abi)

    token_contract = w3.eth.contract(address=CAKE_BSC_ADDRESS, abi=CAKE_BSC_ABI)

    # 设置默认账户，就是发起交易的地址
    w3.eth.defaultAccount = w3.eth.accounts[5]
    file_path = r'C:\WorkFile\3-实验室课题研究\研究-NFT辅助资源共享的无人机网络上的可验证查询\实验数据\Resource_number_on_leaf_node.xlsx'
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    ''''''
    nodeCount = token_contract.functions.getSumTokenTreeNode().call()
    tokenCountList = []
    count = 0
    # 获取叶节点上附着token的数量
    for i in range(0, nodeCount):
        # 获取节点，此处node为元组tuple类型
        node = token_contract.functions.getTheTokenTreeNode(i).call()
        if node[1] == 0:  # node没有子节点，即为叶节点
            tokenCount = token_contract.functions.getTokenIDList(i).call()
            # 写叶节点上附着token的数量
            data.loc[count, 'NormallyIETree'] = len(tokenCount)
            count += 1

    ''''''
    CAKE_BSC_ADDRESS = Web3.toChecksumAddress('0xa8E66dC74546ACed64435A89d71e0c638A87c5a0')
    CAKE_BSC_ABI = json.loads(contract5_abi.abi)
    token_contract = w3.eth.contract(address=CAKE_BSC_ADDRESS, abi=CAKE_BSC_ABI)

    nodeCount = token_contract.functions.getSumTokenTreeNode().call()
    tokenCountList = []

    count = 0
    # 获取叶节点上附着token的数量
    for i in range(0, nodeCount):
        # 获取节点，此处node为元组tuple类型
        node = token_contract.functions.getTheTokenTreeNode(i).call()
        if node[1] == 0:  # node没有子节点，即为叶节点
            tokenCount = token_contract.functions.getTokenIDList(i).call()
            # 写叶节点上附着token的数量
            data.loc[count, 'UniformIETree'] = len(tokenCount)
            count += 1

    ''''''
    CAKE_BSC_ADDRESS = Web3.toChecksumAddress('0x81233Bf8E7516ffb38637ACec5e83d0E761f77Dd')
    CAKE_BSC_ABI = json.loads(contract6_abi.abi)
    token_contract = w3.eth.contract(address=CAKE_BSC_ADDRESS, abi=CAKE_BSC_ABI)

    nodeCount = token_contract.functions.getSumTokenTreeNode().call()
    tokenCountList = []

    count = 0
    # 获取叶节点上附着token的数量
    for i in range(0, nodeCount):
        # 获取节点，此处node为元组tuple类型
        node = token_contract.functions.getTheTokenTreeNode(i).call()
        if node[1] == [0, 0, 0, 0]:  # node没有子节点，即为叶节点
            tokenCount = token_contract.functions.getTokenIDList(i).call()
            # 写叶节点上附着token的数量
            data.loc[count, 'NormallyQuadTree'] = len(tokenCount)
            count += 1

    ''''''
    CAKE_BSC_ADDRESS = Web3.toChecksumAddress('0x35683EF858BaDDAEa48fc4ab13Aef265B91EBDe9')
    CAKE_BSC_ABI = json.loads(contract6_abi.abi)
    token_contract = w3.eth.contract(address=CAKE_BSC_ADDRESS, abi=CAKE_BSC_ABI)
    nodeCount = token_contract.functions.getSumTokenTreeNode().call()
    tokenCountList = []

    count = 0
    # 获取叶节点上附着token的数量
    for i in range(0, nodeCount):
        # 获取节点，此处node为元组tuple类型
        node = token_contract.functions.getTheTokenTreeNode(i).call()
        if node[1] == [0, 0, 0, 0]:  # node没有子节点，即为叶节点
            tokenCount = token_contract.functions.getTokenIDList(i).call()
            # 写叶节点上附着token的数量
            data.loc[count, 'UniformQuadTree'] = len(tokenCount)
            count += 1
    pd.DataFrame(data).to_excel(file_path, index=False)

def drawBuildResult():

    startnum = 0
    endnum = 2500
    node_capacity = 10
    # colorlist = ['r', 'g', 'b', 'y', 'k', 'tan', 'darkorange', 'aquamarine', 'm', 'navy']
    colorlist = ['purple', 'steelblue']
    markerlist = ['3', '3', '4', '4', '.', '.', '+', '+', 'x', 'x']
    file_path_list = [r'C:\WorkFile\服务器实验数据\二分法无倒排构建实验\Normally_IETreeBuild.xlsx',
                      r'C:\WorkFile\服务器实验数据\二分法无倒排构建实验\Normally_QuadTreeBuild.xlsx',
                      r'C:\WorkFile\服务器实验数据\二分法无倒排构建实验\Uniform_IETreeBuild.xlsx',
                      r'C:\WorkFile\服务器实验数据\二分法无倒排构建实验\Uniform_quadTreeBuild.xlsx']
    file_path_list1 = [r'C:\WorkFile\服务器实验数据\订阅查询实验\Normally_IETreeBuild_Subscription.xlsx',
                      r'C:\WorkFile\服务器实验数据\订阅查询实验\Uniform_IETreeBuild_Subscription.xlsx',
                      r'C:\WorkFile\服务器实验数据\订阅查询实验\Uniform_QuadTreeBuild_Subscription.xlsx']
    # 创建画板1，显示正态分布的构建时间
    fig1 = plt.figure(1)  # 如果不传入参数默认画板1
    fig2 = plt.figure(2)
    #legend = ['IE-tree Normal', 'IE-tree Uniform', 'Quad-tree Normal', 'Quad-tree Uniform']
    legend1 = ['Proposed E-tree Normal', 'Quad-tree Normal']
    legend2 = ['Propsoed E-tree Uniform', 'Quad-tree Uniform']
    # 第2步创建画纸，并选择画纸1
    ax1 = fig1.add_subplot(1, 1, 1)
    ax2 = fig2.add_subplot(1, 1, 1)

    subplot = [ax1, ax2]
    # ax5 = fig2.add_subplot(1, 1, 1)
    frontsize=12
    for i in range(0, len(file_path_list)):
        file_path = file_path_list[i]
        data = pd.read_excel(file_path, sheet_name='Sheet1')
        tokenID = data['tokenID'][startnum:endnum]
        time_start = data['time_start'][startnum:endnum]
        time_end = data['time_end'][startnum:endnum]
        node_count = data['node_count'][startnum:endnum]
        layer_count = data['layer_count'][startnum:endnum]

        temptime = time_end - time_start
        accumulative_time = time_end - time_start
        # 过滤time中小于0.5秒的数据，主要观察其中的分裂时间
        temptime = temptime.tolist()
        time = []
        for k in range(0, len(temptime)):
            if temptime[k]>=1.5:
                time.append(temptime[k])


        for j in range(1, len(accumulative_time)):
            accumulative_time[j] += accumulative_time[j - 1]

        subplot[int(i/2)].hist(x=time, bins=20, range=(1.5, 5), weights=[1./len(time)]*len(time),
                               color=colorlist[int(i%2)], alpha = 0.5)

        # subplot[i].text(3.8,0.25,legend[i],fontsize=12,color='k')
        # ax5.plot(tokenID/node_capacity, node_count, color=colorlist[i])

    # ax5.set_xlabel('Number of Resources/Maximum Node Capacity',size=frontsize)
    # ax5.set_ylabel('Total Number of Tree Nodes',size=frontsize)
    # ax5.legend(legend)
    ax1.set_xlabel('Time for Splitting a Node (s)', size=frontsize)
    ax1.set_ylabel('Proportion of Split Nodes', size=frontsize)
    ax1.set_ylim(0, 0.3)
    ax1.set_xlim(1.5, 5)
    ax1.legend(legend1)

    ax2.set_xlabel('Time for Splitting a Node (s)', size=frontsize)
    ax2.set_ylabel('Proportion of Split Nodes', size=frontsize)
    ax2.set_ylim(0, 0.3)
    ax2.set_xlim(1.5, 5)
    ax2.legend(legend2)
    # fig1.subplots_adjust(hspace=0.5)
    # 显示图像
    plt.show()
# 使用seaborn库绘制构建树形结构中节点分裂时间直方图（含概率密度分布曲线）和节点-资源数关系图
def drawBuildResultUseSns():
    startnum = 0
    endnum = 2500
    node_capacity = 10
    # colorlist = ['r', 'g', 'b', 'y', 'k', 'tan', 'darkorange', 'aquamarine', 'm', 'navy']
    # colorlist = ['purple', 'steelblue']
    colorlist = [(214 / 255, 39 / 255, 40 / 255), (44 / 255, 160 / 255, 44 / 255),
                 (31 / 255, 119 / 255, 180 / 255), (255 / 255, 127 / 255, 14 / 255), 'k', 'tan', 'darkorange',
                 'aquamarine', 'm', 'navy']
    markerlist = ['3', '3', '4', '4', '.', '.', '+', '+', 'x', 'x']
    file_path_list = [r'C:\WorkFile\服务器实验数据\二分法无倒排构建实验\Normally_IETreeBuild.xlsx',
                      r'C:\WorkFile\服务器实验数据\二分法无倒排构建实验\Normally_QuadTreeBuild.xlsx',
                      r'C:\WorkFile\服务器实验数据\二分法无倒排构建实验\Uniform_IETreeBuild.xlsx',
                      r'C:\WorkFile\服务器实验数据\二分法无倒排构建实验\Uniform_quadTreeBuild.xlsx']
    file_path_list1 = [r'C:\WorkFile\服务器实验数据\订阅查询实验\Normally_IETreeBuild_Subscription.xlsx',
                       r'C:\WorkFile\服务器实验数据\订阅查询实验\Uniform_IETreeBuild_Subscription.xlsx',
                       r'C:\WorkFile\服务器实验数据\订阅查询实验\Uniform_QuadTreeBuild_Subscription.xlsx']
    # 创建画板1，显示正态分布的构建时间
    fig1 = plt.figure(1)  # 如果不传入参数默认画板1
    fig2 = plt.figure(2)
    fig3 = plt.figure(3)
    fig4 = plt.figure(4)
    legend = ['IE-tree Normal', 'IE-tree Uniform', 'Quad-tree Normal', 'Quad-tree Uniform']
    legend1 = ['Proposed E-tree Normal', 'Quad-tree Normal']
    legend2 = ['Propsoed E-tree Uniform', 'Quad-tree Uniform']
    # 第2步创建画纸，并选择画纸1
    ax1 = fig1.add_subplot(1, 1, 1)
    ax2 = fig2.add_subplot(1, 1, 1)
    subplot = [ax1, ax2]

    ax3 = fig3.add_subplot(1, 1, 1)
    ax4 = fig4.add_subplot(1, 1, 1)
    subplot2 = [ax3, ax4]
    # ax5 = fig2.add_subplot(1, 1, 1)
    # sns.set_palette('hls')
    frontsize = 12
    tokenID_list = []
    node_count_list = []
    for i in range(0, len(file_path_list)):
        file_path = file_path_list[i]
        data = pd.read_excel(file_path, sheet_name='Sheet1')
        tokenID = data['tokenID'][startnum:endnum]
        time_start = data['time_start'][startnum:endnum]
        time_end = data['time_end'][startnum:endnum]
        node_count = data['node_count'][startnum:endnum]
        layer_count = data['layer_count'][startnum:endnum]

        temptime = time_end - time_start
        accumulative_time = time_end - time_start
        # 过滤time中小于0.5秒的数据，主要观察其中的分裂时间
        temptime = temptime.tolist()
        time = []
        for k in range(0, len(temptime)):
            if temptime[k] >= 1.5:
                time.append(temptime[k])

        # 绘制节点分裂时间直方图
        # sns.histplot(time, color=colorlist[int(i % 2)], bins=20, binrange=(1.5,5.0), stat='probability', kde=True, alpha=0.5, legend=True, ax=subplot[int(i / 2)])
        sns.histplot(time, bins=20, binrange=(1.5,5.0), stat='density', kde=False,  alpha=0.2, ax=subplot[int(i / 2)])
        sns.kdeplot(time, ax=subplot[int(i / 2)])
        subplot[int(i / 2)].lines[-1].set_linestyle('--') # stat='density'   stat='percent' line_kws={'linestyle': '--'},
        # sns.kdeplot(x=time, stat='probability', ax=subplot[int(i / 2)])
        # sns.distplot(time, rug=False, hist=False, ax=subplot[int(i / 2)])

        # 删除资源数量增加但节点不增的数据
        tokenID = tokenID.tolist()
        node_count = node_count.tolist()
        j = 1
        while j<len(tokenID):
            if node_count[j]>480:
                tokenID.pop(j)
                node_count.pop(j)
                continue
            if node_count[j-1]==node_count[j]:
                tokenID.pop(j-1)
                node_count.pop(j-1)
            else:
                j += 1
        tokenID_list.append(tokenID)
        node_count_list.append(node_count)
        # 绘制节点数据-资源数量关系图
        subplot2[int(i/2)].plot(node_count, tokenID, color=colorlist[int(i%2)], alpha=0.8)

    # fig1.subplots_adjust(hspace=0.5)
    ax1.set_xlabel('Time for Splitting a Node (s)', size=frontsize)
    ax1.set_ylabel('Proportion of Split Nodes (%)', size=frontsize)
    ax1.set_xlim(1.0, 5.0)
    ax1.set_yticks(np.linspace(0, 1.43057, 6), range(0, 26, 5))
    ax1.set_ylim(0.0, 1.5)
    ax1.legend(legend1)

    ax2.set_xlabel('Time for Splitting a Node (s)', size=frontsize)
    ax2.set_ylabel('Proportion of Split Nodes (%)', size=frontsize)
    ax2.set_xlim(1.0, 5.0)
    ax2.set_yticks(np.linspace(0, 1.4278, 6), range(0, 26, 5))
    ax2.set_ylim(0.0, 1.5)
    ax2.legend(legend2)

    ax3.fill_between(node_count_list[0], tokenID_list[0], 0,  # 上限，下限
                     facecolor=colorlist[3],  # 填充颜色
                     alpha=0.2)  # 透明度
    ax3.fill_between(node_count_list[1], tokenID_list[1], 0,  # 上限，下限
                     facecolor=colorlist[2],  # 填充颜色
                     alpha=0.2)  # 透明度
    ax3.set_xlabel('Number of Nodes', size=frontsize)
    ax3.set_ylabel('Number of Resources', size=frontsize)
    #ax3.set_xlim(1.4, 4.7)
    #ax3.set_ylim(0.0, 0.26)
    ax3.legend(legend1)

    ax4.fill_between(node_count_list[2], tokenID_list[2], 0,  # 上限，下限
                     facecolor=colorlist[3],  # 填充颜色
                     alpha=0.2)  # 透明度
    ax4.fill_between(node_count_list[3], tokenID_list[3], 0,  # 上限，下限
                     facecolor=colorlist[2],  # 填充颜色
                     alpha=0.2)  # 透明度
    ax4.set_xlabel('Number of Nodes', size=frontsize)
    ax4.set_ylabel('Number of Resources', size=frontsize)
    #ax4.set_xlim(1.4, 4.7)
    #ax4.set_ylim(0.0, 0.26)
    ax4.legend(legend2)

    # 显示图像
    plt.show()

def drawBuildResultOld():

    startnum = 0
    endnum = 2500
    node_capacity = 10
    colorlist = ['r', 'g', 'b', 'y', 'k', 'tan', 'darkorange', 'aquamarine', 'm', 'navy']
    markerlist = ['3', '3', '4', '4', '.', '.', '+', '+', 'x', 'x']
    file_path_list = [r'C:\WorkFile\服务器实验数据\二分法无倒排构建实验\Normally_IETreeBuild.xlsx',
                      r'C:\WorkFile\服务器实验数据\二分法无倒排构建实验\Uniform_IETreeBuild.xlsx',
                      r'C:\WorkFile\服务器实验数据\二分法无倒排构建实验\Normally_QuadTreeBuild.xlsx',
                      r'C:\WorkFile\服务器实验数据\二分法无倒排构建实验\Uniform_quadTreeBuild.xlsx']
    file_path_list1 = [r'C:\WorkFile\服务器实验数据\订阅查询实验\Normally_IETreeBuild_Subscription.xlsx',
                      r'C:\WorkFile\服务器实验数据\订阅查询实验\Uniform_IETreeBuild_Subscription.xlsx',
                      r'C:\WorkFile\服务器实验数据\订阅查询实验\Uniform_QuadTreeBuild_Subscription.xlsx']
    # 创建画板1，显示正态分布的构建时间
    fig1 = plt.figure(1)  # 如果不传入参数默认画板1
    fig2 = plt.figure(2)
    legend = ['IE-tree Normal', 'IE-tree Uniform', 'Quad-tree Normal', 'Quad-tree Uniform']
    # 第2步创建画纸，并选择画纸1
    ax1 = fig1.add_subplot(2, 2, 1)
    ax2 = fig1.add_subplot(2, 2, 2)
    ax3 = fig1.add_subplot(2, 2, 3)
    ax4 = fig1.add_subplot(2, 2, 4)

    subplot = [ax1, ax2, ax3, ax4]
    ax5 = fig2.add_subplot(1, 1, 1)
    frontsize=12
    for i in range(0, len(file_path_list)):
        file_path = file_path_list[i]
        data = pd.read_excel(file_path, sheet_name='Sheet1')
        tokenID = data['tokenID'][startnum:endnum]
        time_start = data['time_start'][startnum:endnum]
        time_end = data['time_end'][startnum:endnum]
        node_count = data['node_count'][startnum:endnum]
        layer_count = data['layer_count'][startnum:endnum]

        temptime = time_end - time_start
        accumulative_time = time_end - time_start
        # 过滤time中小于0.5秒的数据，主要观察其中的分裂时间
        temptime = temptime.tolist()
        time = []
        for k in range(0, len(temptime)):
            if temptime[k]>=1.5:
                time.append(temptime[k])


        for j in range(1, len(accumulative_time)):
            accumulative_time[j] += accumulative_time[j - 1]

        subplot[i].hist(x=time, bins=20, range=(1.5, 5), weights=[1./len(time)]*len(time), color='steelblue', edgecolor='black',
                        rwidth= 0.5)
        subplot[i].set_xlabel('Time for Splitting a Node (s)',size=frontsize)
        subplot[i].set_ylabel('Proportion of Split Nodes',size=frontsize)
        subplot[i].set_ylim(0,0.3)
        subplot[i].set_xlim(1.5,5)
        subplot[i].text(3.8,0.25,legend[i],fontsize=12,color='k')
        ax5.plot(tokenID/node_capacity, node_count, color=colorlist[i])

    ax5.set_xlabel('Number of Resources/Maximum Node Capacity',size=frontsize)
    ax5.set_ylabel('Total Number of Tree Nodes',size=frontsize)
    ax5.legend(legend)

    # 显示图像
    plt.show()

def drawBuildQueryTreeResultOld():

    startnum = 0
    endnum = 100
    node_capacity = 5
    colorlist = ['r', 'g', 'b', 'y', 'k', 'tan', 'darkorange', 'aquamarine', 'm', 'navy']
    markerlist = ['3', '3', '4', '4', '.', '.', '+', '+', 'x', 'x']
    file_path_list = [r'C:\WorkFile\服务器实验数据\订阅查询实验\Normally_IETreeBuild_Subscription.xlsx',
                      r'C:\WorkFile\服务器实验数据\订阅查询实验\Uniform_IETreeBuild_Subscription.xlsx',
                      r'C:\WorkFile\服务器实验数据\订阅查询实验\Uniform_QuadTreeBuild_Subscription.xlsx']
    # 创建画板1，显示正态分布的构建时间
    fig1 = plt.figure(1)  # 如果不传入参数默认画板1
    fig2 = plt.figure(2)
    legend = ['IE-tree Normal', 'IE-tree Uniform', 'Quad-tree Uniform']
    # 第2步创建画纸，并选择画纸1
    ax1 = fig1.add_subplot(1, 3, 1)
    ax2 = fig1.add_subplot(1, 3, 2)
    ax3 = fig1.add_subplot(1, 3, 3)
    subplot = [ax1, ax2, ax3]
    ax5 = fig2.add_subplot(1, 1, 1)
    frontsize=12
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
            if temptime[k]>=4.5:
                time.append(temptime[k])


        for j in range(1, len(accumulative_time)):
            accumulative_time[j] += accumulative_time[j - 1]

        subplot[i].hist(x=time, bins=20, range=(4.5, 10), weights=[1./len(time)]*len(time), color='steelblue', edgecolor='black',
                        rwidth= 0.5)
        subplot[i].set_xlabel('Time for Splitting a Node (s)', size=frontsize)
        subplot[i].set_ylabel('Proportion of Split Nodes', size=frontsize)
        subplot[i].set_ylim(0,0.25)
        subplot[i].set_xlim(4.5,10)
        subplot[i].text(6.5,0.22,legend[i],fontsize=12,color='k')
        ax5.plot(queryID, node_count, color=colorlist[i])

    ax5.set_xlabel('Number of Resources/Maximum Node Capacity', size=frontsize)
    ax5.set_ylabel('Total Number of Tree Nodes', size=frontsize)
    ax5.legend(legend)
    fig1.subplots_adjust(wspace=0.5)
    # 显示图像
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
    frontsize=12
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
            if temptime[k]>=4.5:
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

        sns.histplot(time, bins=30, binrange=(4.5, 10.0), stat='density', kde=False, hatch=hatchlist[i], alpha=0.2, ax=ax5)
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
        print(node_count[len(node_count)-1])

        # 绘制节点数据-资源数量关系图
        ax6.plot(node_count, queryID, color=colorlist[i], alpha=0.8)

    ax5.set_xlabel('Time for Splitting a Node (s)', size=frontsize)
    ax5.set_ylabel('Proportion of Split Nodes (%)', size=frontsize)
    ax5.set_yticks(np.linspace(0, 1.36489, 6), range(0, 26, 5))
    ax5.set_xlim(4,10)
    ax5.set_ylim(0,1.22)
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

def drawCalculatedRatioOfLeafNode():
    file_path = r'C:\WorkFile\服务器实验数据\叶节点负载统计实验\Resource_number_on_leaf_node_IE_Normal.xlsx'
    data = pd.read_excel(file_path, sheet_name='Sheet1')

    # 正态分布IE-tree
    data_x1 = data['NormallyIETree'].tolist()
    i = 0
    while i < len(data_x1):
        if data_x1[i] == data_x1[i]:
            data_x1[i] = int(data_x1[i])
            i += 1
        else:
            data_x1.pop(i)

    # 均匀分布IE-tree
    file_path = r'C:\WorkFile\服务器实验数据\叶节点负载统计实验\Resource_number_on_leaf_node_IE_Uniform.xlsx'
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    data_x2 = data['UniformIETree'].tolist()
    i = 0
    while i < len(data_x2):
        if data_x2[i] == data_x2[i]:
            data_x2[i] = int(data_x2[i])
            i += 1
        else:
            data_x2.pop(i)

    # 正态分布quad-tree
    file_path = r'C:\WorkFile\服务器实验数据\叶节点负载统计实验\Resource_number_on_leaf_node_Quad_Normal.xlsx'
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    data_x3 = data['NormallyQuadTree'].tolist()
    i = 0
    while i < len(data_x3):
        if data_x3[i] == data_x3[i]:
            data_x3[i] = int(data_x3[i])
            i += 1
        else:
            data_x3.pop(i)

    # 均匀分布quad-tree Resource_number_on_leaf_node_Quad_Uniform
    file_path = r'C:\WorkFile\服务器实验数据\叶节点负载统计实验\Resource_number_on_leaf_node_Quad_Uniform.xlsx'
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    data_x4 = data['UniformQuadTree'].tolist()
    i = 0
    while i < len(data_x4):
        if data_x4[i] == data_x4[i]:
            data_x4[i] = int(data_x4[i])
            i += 1
        else:
            data_x4.pop(i)

    # 统计各种情况下的叶节点关联资源数量
    labels = []
    countDict_1 = dict()
    proportitionDict_1 = dict()
    for i in set(data_x1):
        countDict_1[i] = data_x1.count(i)
        proportitionDict_1[i] = data_x1.count(i) / len(data_x1)*100
        labels.append(i)

    countDict_2 = dict()
    proportitionDict_2 = dict()
    for i in set(data_x2):
        countDict_2[i] = data_x2.count(i)
        proportitionDict_2[i] = data_x2.count(i) / len(data_x2)*100
        labels.append(i)

    countDict_3 = dict()
    proportitionDict_3 = dict()
    for i in set(data_x3):
        countDict_3[i] = data_x3.count(i)
        proportitionDict_3[i] = data_x3.count(i) / len(data_x3)*100
        labels.append(i)

    countDict_4 = dict()
    proportitionDict_4 = dict()
    for i in set(data_x4):
        countDict_4[i] = data_x4.count(i)
        proportitionDict_4[i] = data_x4.count(i) / len(data_x4)*100
        labels.append(i)

    labels = list(set(labels))
    labels.sort()
    data_x1.clear()
    data_x2.clear()
    data_x3.clear()
    data_x4.clear()

    for i in range(0, len(labels)):
        if (labels[i] in proportitionDict_1):
            data_x1.append(proportitionDict_1[labels[i]])
        else:
            data_x1.append(0)

        if (labels[i] in proportitionDict_2):
            data_x2.append(proportitionDict_2[labels[i]])
        else:
            data_x2.append(0)

        if (labels[i] in proportitionDict_3):
            data_x3.append(proportitionDict_3[labels[i]])
        else:
            data_x3.append(0)

        if (labels[i] in proportitionDict_4):
            data_x4.append(proportitionDict_4[labels[i]])
        else:
            data_x4.append(0)


    # 柱状图
    x = np.arange(len(labels))  # x轴刻度标签位置
    labels = np.array(labels)
    labels = (labels/10)*100
    labels = labels.tolist()
    label = []
    for i in range(0,len(labels)):
        label.append(int(labels[i]))
    width = 0.16  # 柱子的宽度
    # 计算每个柱子在x轴上的位置，保证x轴刻度标签居中
    plt.bar(x - 1.5 * width, data_x1, width, label='1')
    plt.bar(x - 0.5 * width, data_x2, width, label='2')
    plt.bar(x + 0.5 * width, data_x3, width, label='3')
    plt.bar(x + 1.5 * width, data_x4, width, label='4')

    # x轴刻度标签位置不进行计算
    frontsize = 12
    plt.xticks(x, labels=label)
    legend = ['IE-tree normal', 'IE-tree uniform', 'Quad-tree normal', 'Quad-tree uniform']
    plt.legend(legend,loc='upper left')
    plt.xlabel('Resource Capacity Ratio(%)', size=frontsize)
    plt.ylabel('Proportion of Leaf Nodes(%)', size=frontsize)
    plt.show()
# 使用seaborn库绘制叶节点容量使用率密度分布图
def drawCalculatedRatioOfLeafNodeUseSns():

    fig1 = plt.figure(1)
    ax1 = fig1.add_subplot(1, 1, 1)
    fig2 = plt.figure(2)
    ax2 = fig2.add_subplot(1, 1, 1)

    file_path = r'C:\WorkFile\服务器实验数据\叶节点负载统计实验\Resource_number_on_leaf_node_IE_Normal.xlsx'
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    sns.histplot(data['NormallyIETree'], bins=11, binrange=(0, 11), stat='density', kde=False, alpha=0.2, ax=ax1)
    sns.kdeplot(data['NormallyIETree'], ax=ax1)
    ax1.lines[-1].set_linestyle('--')  # stat='density'   stat='percent'  line_kws={'linestyle': '--'}

    file_path = r'C:\WorkFile\服务器实验数据\叶节点负载统计实验\Resource_number_on_leaf_node_Quad_Normal.xlsx'
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    sns.histplot(data['NormallyQuadTree'], bins=11, binrange=(0, 11), stat='density', kde=False, alpha=0.2, ax=ax1)
    sns.kdeplot(data['NormallyQuadTree'], ax=ax1)
    ax1.lines[-1].set_linestyle('--')  # stat='density'   stat='percent'  line_kws={'linestyle': '--'}

    ax1.legend(['Proposed E-Tree Normal', 'Quad-Tree Normal'])
    ax1.set_xlabel('Resource Capacity Ratio (%)')
    ax1.set_ylabel('Proportion of Leaf Nodes (%)')
    ax1.set_xticks(np.linspace(0.5,10.5,11),range(0,110,10))
    ax1.set_yticks(np.linspace(0,0.25,6),range(0,26,5))
    ax1.set_xlim(-0.5,11.5)
    ax1.set_ylim(0, 0.27)
    #plt.show()


    file_path = r'C:\WorkFile\服务器实验数据\叶节点负载统计实验\Resource_number_on_leaf_node_IE_Uniform.xlsx'
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    sns.histplot(data['UniformIETree'], bins=11, binrange=(0, 11), stat='density', kde=False, alpha=0.2, ax=ax2)
    sns.kdeplot(data['UniformIETree'], ax=ax2)
    ax2.lines[-1].set_linestyle('--')  # stat='density'   stat='percent'  line_kws={'linestyle': '--'}

    file_path = r'C:\WorkFile\服务器实验数据\叶节点负载统计实验\Resource_number_on_leaf_node_Quad_Uniform.xlsx'
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    sns.histplot(data['UniformQuadTree'], bins=11, binrange=(0, 11), stat='density', kde=False, alpha=0.2, ax=ax2)
    sns.kdeplot(data['UniformQuadTree'], ax=ax2)
    ax2.lines[-1].set_linestyle('--')  # stat='density'   stat='percent'  line_kws={'linestyle': '--'}

    ax2.legend(['Proposed E-Tree Uniform', 'Quad-Tree Uniform'])
    ax2.set_xlabel('Resource Capacity Ratio (%)')
    ax2.set_ylabel('Proportion of Leaf Nodes (%)')
    ax2.set_xticks(np.linspace(0.5, 10.5, 11), range(0, 110, 10))
    ax2.set_yticks(np.linspace(0, 0.25, 6), range(0, 26, 5))
    ax2.set_xlim(-0.5, 11.5)
    ax2.set_ylim(0, 0.27)
    plt.show()

def drawQueryTime_old():
    # 从磁盘读取数据excel
    file_path = r'C:\WorkFile\3-实验室课题研究\研究-NFT辅助资源共享的无人机网络上的可验证查询\实验数据\Normally_IETreeQuery.xlsx'
    data = pd.read_excel(file_path, sheet_name='Sheet1')

    N_IE_queryNo = data['queryNo']
    time_start = data['time_start']
    time_end = data['time_end']

    # 处理时间数据
    N_IE_time = time_end - time_start
    N_IE_accumulative_time = time_end - time_start
    for i in range(1, len(N_IE_accumulative_time)):
        N_IE_accumulative_time[i] += N_IE_accumulative_time[i - 1]

    file_path = r'C:\WorkFile\3-实验室课题研究\研究-NFT辅助资源共享的无人机网络上的可验证查询\实验数据\Normally_QuadTreeQuery.xlsx'
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    N_quad_queryNo = data['queryNo']
    time_start = data['time_start']
    time_end = data['time_end']

    N_quad_time = time_end - time_start
    N_quad_accumulative_time = time_end - time_start
    for i in range(1, len(N_quad_accumulative_time)):
        N_quad_accumulative_time[i] += N_quad_accumulative_time[i - 1]

    file_path = r'C:\WorkFile\3-实验室课题研究\研究-NFT辅助资源共享的无人机网络上的可验证查询\实验数据\Uniform_IETreeQuery.xlsx'
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    U_IE_queryNo = data['queryNo']
    time_start = data['time_start']
    time_end = data['time_end']

    U_IE_time = time_end - time_start
    U_IE_accumulative_time = time_end - time_start
    for i in range(1, len(U_IE_accumulative_time)):
        U_IE_accumulative_time[i] += U_IE_accumulative_time[i - 1]

    file_path = r'C:\WorkFile\3-实验室课题研究\研究-NFT辅助资源共享的无人机网络上的可验证查询\实验数据\Uniform_QuadTreeQuery.xlsx'
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    U_quad_queryNo = data['queryNo']
    time_start = data['time_start']
    time_end = data['time_end']

    U_quad_time = time_end - time_start
    U_quad_accumulative_time = time_end - time_start
    for i in range(1, len(U_quad_accumulative_time)):
        U_quad_accumulative_time[i] += U_quad_accumulative_time[i - 1]

    file_path = r'C:\WorkFile\3-实验室课题研究\研究-NFT辅助资源共享的无人机网络上的可验证查询\实验数据\Normally_QuadTreeQuery(BigRange).xlsx'
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    NBR_quad_queryNo = data['queryNo']
    time_start = data['time_start']
    time_end = data['time_end']

    NBR_quad_time = time_end - time_start
    NBR_quad_accumulative_time = time_end - time_start
    for i in range(1, len(NBR_quad_accumulative_time)):
        NBR_quad_accumulative_time[i] += NBR_quad_accumulative_time[i - 1]

    # 创建画板1，显示正态分布的构建时间
    fig = plt.figure(1)  # 如果不传入参数默认画板1
    legend = ['IE-tree normal', 'Quad-tree normal', 'IE-tree uniform', 'Quad-tree uniform', 'Quad-tree normal(big range']
    # 第2步创建画纸，并选择画纸1
    ax1 = plt.subplot(1, 2, 1)
    ax2 = plt.subplot(1, 2, 2)

    ax1.scatter(N_IE_queryNo, N_IE_time, s=5, color='g', marker='x')
    ax1.scatter(N_quad_queryNo, N_quad_time, s=5, color='b', marker='+')
    ax1.scatter(U_IE_queryNo, U_IE_time, s=5, color='y', marker='*')
    ax1.scatter(U_quad_queryNo, U_quad_time, s=5, color='r', marker='d')
    ax1.scatter(NBR_quad_queryNo,NBR_quad_time, s=5, color='darkorange', marker='3')
    ax1.set_xlabel('Query Sequence')
    ax1.set_ylabel('CPU Time (s)')
    ax1.legend(legend)

    ax2.plot(N_IE_queryNo, N_IE_accumulative_time, color='g', marker='x')
    ax2.plot(N_quad_queryNo, N_quad_accumulative_time, color='b', marker='+')
    ax2.plot(U_IE_queryNo, U_IE_accumulative_time, color='y', marker='*')
    ax2.plot(U_quad_queryNo, U_quad_accumulative_time, color='r', marker='d')
    ax2.plot(NBR_quad_queryNo, NBR_quad_accumulative_time, color='darkorange', marker='3')
    ax2.set_xlabel('Query Sequence')
    ax2.set_ylabel('Accumulative CPU Time (s)')
    ax2.legend(legend)

    plt.show()
# 分批注入2500个资源数据，每500个时执行一组（50）个查询，取每组查询累计值，绘制线图
def drawQueryTime():
    # 创建画板1，显示正态分布的构建时间
    fig = plt.figure(1)  # 如果不传入参数默认画板1
    # 第2步创建画纸，并选择画纸1
    ax1 = plt.subplot(1, 2, 1)
    ax2 = plt.subplot(1, 2, 2)
    ax1.set_xlabel('Query Sequence')
    ax1.set_ylabel('Accumulative CPU Time (s)')
    ax2.set_xlabel('Query Sequence')
    ax2.set_ylabel('Accumulative CPU Time (s)')

    colorlist = ['r', 'g', 'b', 'y', 'k', 'tan', 'darkorange', 'aquamarine', 'm', 'navy']
    markerlist = ['3', '3', '4', '4', '.', '.', '+', '+', 'x', 'x']
    legend1 = ['Proposed E-tree normal',  'Quad-tree normal']
    legend2 = ['Proposed E-tree uniform', 'Quad-tree uniform']

    file_path_list1 = [[r'C:\WorkFile\服务器实验数据\第二次四种情况的单次查询结果\Normally_ETreeQuery_500.xlsx',
                       r'C:\WorkFile\服务器实验数据\第二次四种情况的单次查询结果\Normally_ETreeQuery_1000.xlsx',
                       r'C:\WorkFile\服务器实验数据\第二次四种情况的单次查询结果\Normally_ETreeQuery_1500.xlsx',
                       r'C:\WorkFile\服务器实验数据\第二次四种情况的单次查询结果\Normally_ETreeQuery_2000.xlsx',
                       r'C:\WorkFile\服务器实验数据\第二次四种情况的单次查询结果\Normally_ETreeQuery_2500.xlsx'],

                      [r'C:\WorkFile\服务器实验数据\第二次四种情况的单次查询结果\Normally_QuadTreeQuery_500.xlsx',
                       r'C:\WorkFile\服务器实验数据\第二次四种情况的单次查询结果\Normally_QuadTreeQuery_1000.xlsx',
                       r'C:\WorkFile\服务器实验数据\第二次四种情况的单次查询结果\Normally_QuadTreeQuery_1500.xlsx',
                       r'C:\WorkFile\服务器实验数据\第二次四种情况的单次查询结果\Normally_QuadTreeQuery_2000.xlsx',
                       r'C:\WorkFile\服务器实验数据\第二次四种情况的单次查询结果\Normally_QuadTreeQuery_2500.xlsx']]

    file_path_list2 = [[r'C:\WorkFile\服务器实验数据\第二次四种情况的单次查询结果\Uniform_ETreeQuery_500.xlsx',
                        r'C:\WorkFile\服务器实验数据\第二次四种情况的单次查询结果\Uniform_ETreeQuery_1000.xlsx',
                        r'C:\WorkFile\服务器实验数据\第二次四种情况的单次查询结果\Uniform_ETreeQuery_1500.xlsx',
                        r'C:\WorkFile\服务器实验数据\第二次四种情况的单次查询结果\Uniform_ETreeQuery_2000.xlsx',
                        r'C:\WorkFile\服务器实验数据\第二次四种情况的单次查询结果\Uniform_ETreeQuery_2500.xlsx'],

                       [r'C:\WorkFile\服务器实验数据\第二次四种情况的单次查询结果\Uniform_QuadTreeQuery_500.xlsx',
                        r'C:\WorkFile\服务器实验数据\第二次四种情况的单次查询结果\Uniform_QuadTreeQuery_1000.xlsx',
                        r'C:\WorkFile\服务器实验数据\第二次四种情况的单次查询结果\Uniform_QuadTreeQuery_1500.xlsx',
                        r'C:\WorkFile\服务器实验数据\第二次四种情况的单次查询结果\Uniform_QuadTreeQuery_2000.xlsx',
                        r'C:\WorkFile\服务器实验数据\第二次四种情况的单次查询结果\Uniform_QuadTreeQuery_2500.xlsx']]

    E_time=[]
    Time = []
    for i in range(0, len(file_path_list1)):
        AccTime = []
        for k in range(0, len(file_path_list1[i])):
            file_path = file_path_list1[i][k]
            data = pd.read_excel(file_path, sheet_name='Sheet1')
            time_start = data['time_start']
            time_end = data['time_end']
            # 处理时间数据
            accumulative_time = time_end - time_start
            for j in range(1, len(accumulative_time)):
                accumulative_time[j] += accumulative_time[j - 1]
            AccTime.append(accumulative_time[len(accumulative_time)-1])

        Time.append(AccTime)

    print(Time)
    data_x = [500,1000,1500,2000,2500]
    for i in range(0,len(file_path_list1)):
        ax1.plot(data_x, Time[i],color=colorlist[i])

    ax1.legend(legend1)

    Q_time = []
    Time = []
    for i in range(0, len(file_path_list2)):
        AccTime = []
        for k in range(0, len(file_path_list2[i])):
            file_path = file_path_list2[i][k]
            data = pd.read_excel(file_path, sheet_name='Sheet1')
            time_start = data['time_start']
            time_end = data['time_end']
            # 处理时间数据
            accumulative_time = time_end - time_start
            for j in range(1, len(accumulative_time)):
                accumulative_time[j] += accumulative_time[j - 1]
            AccTime.append(accumulative_time[len(accumulative_time) - 1])
        Time.append(AccTime)

    print(Time)
    data_x = [500, 1000, 1500, 2000, 2500]
    for i in range(0, len(file_path_list2)):
        ax2.plot(data_x, Time[i], color=colorlist[i])

    ax2.legend(legend2)

    plt.show()

# 分批注入2500个资源数据，每500个时执行一组（50）个查询，E-tree每组取最小值，Quad-tree每组取最大值，绘制线图
def drawQueryTimeMaxMinMean():
    # 创建画板1，显示正态分布的构建时间
    fig1 = plt.figure(1)  # 如果不传入参数默认画板1
    fig2 = plt.figure(2)
    # 第2步创建画纸，并选择画纸1
    frontsize = 12
    ax1 = fig1.add_subplot(1, 1, 1)
    ax2 = fig2.add_subplot(1, 1, 1)
    ax1.set_xlabel('Number of blocks', size=frontsize)
    ax1.set_ylabel('Accumulative CPU Time (s)', size=frontsize)
    ax2.set_xlabel('Number of blocks', size=frontsize)
    ax2.set_ylabel('Accumulative CPU Time (s)', size=frontsize)

    colorlist = [(214 / 255, 39 / 255, 40 / 255), (44 / 255, 160 / 255, 44 / 255),
                 (31 / 255, 119 / 255, 180 / 255), (255 / 255, 127 / 255, 14 / 255), 'k', 'tan', 'darkorange', 'aquamarine', 'm', 'navy']
    markerlist = ['^', '.', '.', '+', '+', 'x', 'x']
    legend1 = ['Proposed E-tree normal', 'Quad-tree normal']
    legend2 = ['Proposed E-tree uniform', 'Quad-tree uniform']
    file_name = '第三次单次查询实验结果'

    file_path_list1 = [[r'C:\WorkFile\服务器实验数据\{}\Normally_ETreeQuery_500.xlsx'.format(file_name),
                        r'C:\WorkFile\服务器实验数据\{}\Normally_ETreeQuery_1000.xlsx'.format(file_name),
                        r'C:\WorkFile\服务器实验数据\{}\Normally_ETreeQuery_1500.xlsx'.format(file_name),
                        r'C:\WorkFile\服务器实验数据\{}\Normally_ETreeQuery_2000.xlsx'.format(file_name),
                        r'C:\WorkFile\服务器实验数据\{}\Normally_ETreeQuery_2500.xlsx'.format(file_name)],

                       [r'C:\WorkFile\服务器实验数据\{}\Uniform_ETreeQuery_500.xlsx'.format(file_name),
                        r'C:\WorkFile\服务器实验数据\{}\Uniform_ETreeQuery_1000.xlsx'.format(file_name),
                        r'C:\WorkFile\服务器实验数据\{}\Uniform_ETreeQuery_1500.xlsx'.format(file_name),
                        r'C:\WorkFile\服务器实验数据\{}\Uniform_ETreeQuery_2000.xlsx'.format(file_name),
                        r'C:\WorkFile\服务器实验数据\{}\Uniform_ETreeQuery_2500.xlsx'.format(file_name)]]

    file_path_list2 = [[r'C:\WorkFile\服务器实验数据\{}\Normally_QuadTreeQuery_500.xlsx'.format(file_name),
                        r'C:\WorkFile\服务器实验数据\{}\Normally_QuadTreeQuery_1000.xlsx'.format(file_name),
                        r'C:\WorkFile\服务器实验数据\{}\Normally_QuadTreeQuery_1500.xlsx'.format(file_name),
                        r'C:\WorkFile\服务器实验数据\{}\Normally_QuadTreeQuery_2000.xlsx'.format(file_name),
                        r'C:\WorkFile\服务器实验数据\{}\Normally_QuadTreeQuery_2500.xlsx'.format(file_name)],

                       [r'C:\WorkFile\服务器实验数据\{}\Uniform_QuadTreeQuery_500.xlsx'.format(file_name),
                        r'C:\WorkFile\服务器实验数据\{}\Uniform_QuadTreeQuery_1000.xlsx'.format(file_name),
                        r'C:\WorkFile\服务器实验数据\{}\Uniform_QuadTreeQuery_1500.xlsx'.format(file_name),
                        r'C:\WorkFile\服务器实验数据\{}\Uniform_QuadTreeQuery_2000.xlsx'.format(file_name),
                        r'C:\WorkFile\服务器实验数据\{}\Uniform_QuadTreeQuery_2500.xlsx'.format(file_name)]]

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

    data_x = [500, 1000, 1500, 2000, 2500]
    '''
    ax1.plot(data_x, E_time[0], color=colorlist[0], marker=markerlist[0])
    ax1.plot(data_x, Q_time[0], color=colorlist[1], marker=markerlist[1])
    ax1.set_ylim(0.0, 1.0)
    ax1.set_xticks(range(500, 2501, 500), data_x)
    ax1.legend(legend1, loc='upper left')

    ax3 = ax1.twinx()
    ax3.plot(data_x, np.array(Q_time[0]) - np.array(E_time[0]), color=colorlist[2], linestyle='--')
    ax3.fill_between(data_x, np.array(Q_time[0]) - np.array(E_time[0]), 0, # 上限，下限
                     facecolor=colorlist[2],  # 填充颜色
                     alpha=0.3)  # 透明度

    ax3.set_ylim(-0.1, 0.5)
    ax3.set_ylabel('Time Difference (s)', size=frontsize)
    ax3.legend(['Time Difference'], loc='lower right')

    ax2.plot(data_x, E_time[1], color=colorlist[0], marker=markerlist[0])
    ax2.plot(data_x, Q_time[1], color=colorlist[1], marker=markerlist[1])
    ax2.set_ylim(0.0, 1.0)
    ax2.set_xticks(range(500, 2501, 500), data_x)
    ax2.legend(legend2, loc='upper left')

    ax4 = ax2.twinx()
    ax4.plot(data_x, np.array(Q_time[1]) - np.array(E_time[1]), color=colorlist[2], linestyle='--')
    ax4.fill_between(data_x, np.array(Q_time[1]) - np.array(E_time[1]), 0, # 上限，下限
                     facecolor=colorlist[2],  # 填充颜色
                     alpha=0.3)  # 透明度

    ax4.set_ylim(-0.1, 0.5)
    ax4.set_ylabel('Time Difference (s)', size=frontsize)
    ax4.legend(['Time Difference'], loc='lower right')'''
    ''''''
    # 柱状图
    x = np.arange(5)  # x轴刻度标签位置
    width = 0.4  # 柱子的宽度

    # 计算每个柱子在x轴上的位置，保证x轴刻度标签居中
    ax1.bar(x - 0.5 * width, E_time[0], width, color=colorlist[2], edgecolor='k', hatch='xx', alpha=0.5)
    ax1.bar(x + 0.5 * width, Q_time[0], width, color=colorlist[3], edgecolor='k', hatch='//', alpha=0.5)
    ax1.set_ylim(0.0, 1.0)
    ax1.set_xticks(x, labels=data_x)
    ax1.legend(legend1, loc='upper left')

    ax2.bar(x - 0.5 * width, E_time[1], width, color=colorlist[2], edgecolor='k', hatch='xx', alpha=0.5)
    ax2.bar(x + 0.5 * width, Q_time[1], width, color=colorlist[3], edgecolor='k', hatch='//', alpha=0.5)
    ax2.set_ylim(0.0, 1.0)
    ax2.set_xticks(x, labels=data_x)
    ax2.legend(legend2, loc='upper left')



    plt.show()


# 注入500个资源数据，执行50次查询，绘制50次累计时间线图
def drawQueryTime500():

    start=0
    end=20
    colorlist = [(214/255,39/255,40/255), (44/255,160/255,44/255),
                 (31/255,119/255,180/255), (255/255,127/255,14/255), 'k', 'tan', 'darkorange', 'aquamarine', 'm', 'navy']
    markerlist = ['^', '.', '.', '+', '+', 'x', 'x']
    legend = ['Proposed E-tree normal', 'Proposed E-tree uniform', 'Quad-tree normal', 'Quad-tree uniform']

    file_path_list1 = [r'C:\WorkFile\服务器实验数据\二分法查询实验（500）\Normally_IETreeQuery_500_Min_fan7.xlsx',
                       r'C:\WorkFile\服务器实验数据\二分法查询实验（500）\Normally_QuadTreeQuery_500.xlsx',
                       r'C:\WorkFile\服务器实验数据\二分法查询实验（500）\Uniform_IETreeQuery_500_Min_fan7.xlsx',
                       r'C:\WorkFile\服务器实验数据\二分法查询实验（500）\Uniform_QuadTreeQuery_500.xlsx']

    # 创建画板1，显示正态分布的构建时间
    fig1 = plt.figure(1)  # 如果不传入参数默认画板1
    fig2 = plt.figure(2)
    # legend = ['IE-tree Normal', 'IE-tree Uniform', 'Quad-tree Normal', 'Quad-tree Uniform']
    legend1 = ['Proposed E-tree Normal', 'Quad-tree Normal']
    legend2 = ['Propsoed E-tree Uniform', 'Quad-tree Uniform']
    # 第2步创建画纸，并选择画纸1
    ax1 = fig1.add_subplot(1, 1, 1)
    ax2 = fig2.add_subplot(1, 1, 1)
    subplot = [ax1, ax2]
    frontsize = 12

    accumulative_time_list = []

    for i in range(0, len(file_path_list1)):
        file_path = file_path_list1[i]
        data = pd.read_excel(file_path, sheet_name='Sheet1')
        queryNo = data['queryNo'][start:end]
        time_start = data['time_start'][start:end]
        time_end = data['time_end'][start:end]
        # 处理时间数据

        accumulative_time = time_end - time_start
        for j in range(1, len(accumulative_time)):
            accumulative_time[j] += accumulative_time[j - 1]

        accumulative_time_list.append(accumulative_time)
        subplot[int(i / 2)].plot(queryNo, accumulative_time, color=colorlist[int(i % 2)],
                                 marker=markerlist[int(i%2)], alpha=1)

    ax1.set_xlabel('Query Sequence', size=frontsize)
    ax1.set_ylabel('Accumulative Query CPU Time (s)', size=frontsize)
    ax1.set_ylim(0, 14)
    ax1.set_xticks(range(1, 20, 2), range(2, 21, 2))
    ax1.legend(legend1)

    ax2.set_xlabel('Query Sequence', size=frontsize)
    ax2.set_ylabel('Accumulative Query CPU Time (s)', size=frontsize)
    ax2.set_ylim(0, 14)
    ax2.set_xticks(range(1, 20, 2), range(2, 21, 2))
    ax2.legend(legend2)

    # 绘制右纵坐标的时间差线图阴影
    ax3 = ax1.twinx()
    ax3.plot(range(0,20,1), accumulative_time_list[1]-accumulative_time_list[0], color=colorlist[2], linestyle='--')
    ax3.fill_between(range(0,20,1), accumulative_time_list[1]-accumulative_time_list[0], 0,  # 上限，下限
                     facecolor=colorlist[2],  # 填充颜色
                     alpha=0.3)  # 透明度

    ax3.set_ylim(0, 2.5)
    ax3.set_ylabel('Time Difference (s)', size=frontsize)
    ax3.legend(['Time Difference'], loc='lower right')

    ax4 = ax2.twinx()
    ax4.plot(range(0, 20, 1), accumulative_time_list[3] - accumulative_time_list[2], color=colorlist[2],
             linestyle='--')
    ax4.fill_between(range(0, 20, 1), accumulative_time_list[3] - accumulative_time_list[2], 0,  # 上限，下限
                     facecolor=colorlist[2],  # 填充颜色
                     alpha=0.3)  # 透明度

    ax4.set_ylim(0, 2.5)
    ax4.set_ylabel('Time Difference (s)', size=frontsize)
    ax4.legend(['Time Difference'], loc='lower right')

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

def drawIETreeFanBuildResult():

    # 创建画板1，显示正态分布的构建时间
    fig = plt.figure(1)  # 如果不传入参数默认画板1
    legend = ['Fan=4', 'Fan=5', 'Fan=6', 'Fan=7', 'Fan=8', 'Fan=9', 'Fan=10', 'Fan=11', 'Fan=12', 'Fan=13']
    # 第2步创建画纸，并选择画纸1
    ax1 = plt.subplot(2, 2, 1)
    ax2 = plt.subplot(2, 2, 2)
    ax3 = plt.subplot(2, 2, 3)
    ax4 = plt.subplot(2, 2, 4)

    ax1.set_xlabel('Resource Sequence')
    ax1.set_ylabel('CPU Time - Full Node(s)')
    ax1.legend(legend)
    ax2.set_xlabel('Resource Count')
    ax2.set_ylabel('Accumulate CPU Time - Full Node (s)')
    ax2.legend(legend)
    ax3.set_xlabel('Number of Resources/Node Capacity')
    ax3.set_ylabel('Total Number of Tree Nodes')
    ax3.legend(legend)
    ax4.set_xlabel('Number of Resources/Node Capacity')
    ax4.set_ylabel('Tree Height')
    ax4.legend(legend)

    num = 3000
    colorlist = ['r', 'g', 'b', 'y', 'k', 'tan', 'darkorange', 'aquamarine', 'm', 'navy']
    markerlist = ['3', '3', '4', '4', '.', '.', '+', '+', 'x', 'x']
    sequencelist = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    for i in range(0, 10):
        file_path = r'C:\WorkFile\服务器实验数据\扇出实验\Normal_IETreeBuild_fan{}.xlsx'.format(sequencelist[i])
        data = pd.read_excel(file_path, sheet_name='Sheet1')
        N_IE_tokenID = data['tokenID'][0:num]
        time_start = data['time_start'][0:num]
        time_end = data['time_end'][0:num]
        N_IE_node_count = data['node_count'][0:num]
        N_IE_layer_count = data['layer_count'][0:num]

        N_IE_time = time_end - time_start
        N_IE_accumulative_time = time_end - time_start
        for j in range(1, len(N_IE_accumulative_time)):
            N_IE_accumulative_time[j] += N_IE_accumulative_time[j - 1]

        ax1.scatter(N_IE_tokenID, N_IE_time, s=3, color=colorlist[i], marker=markerlist[i])
        ax2.plot(N_IE_tokenID, N_IE_accumulative_time, color=colorlist[i], marker=markerlist[i])
        ax3.plot(N_IE_tokenID / 10, N_IE_node_count, color=colorlist[i])
        ax4.plot(N_IE_tokenID / 10, N_IE_layer_count, color=colorlist[i])

    # 显示图像
    plt.show()

def drawDoubleYIETreeFanBuildResult():
    num = 2500
    colorlist = ['r', 'g', 'b', 'y', 'k', 'tan', 'darkorange', 'aquamarine', 'm', 'navy']
    markerlist = ['3', '3', '4', '4', '.', '.', '+', '+', 'x', 'x']
    sequencelist = [4, 5, 6, 7, 8, 9,10,11,12,13]
    accumulative_time = []
    total_node = []
    for i in range(0, 10):
        file_path = r'C:\WorkFile\服务器实验数据\二分法扇出实验\Normally_IETreeBuild_fan{}.xlsx'.format(sequencelist[i])
        data = pd.read_excel(file_path, sheet_name='Sheet1')
        N_IE_tokenID = data['tokenID'][0:num]
        time_start = data['time_start'][0:num]
        time_end = data['time_end'][0:num]
        N_IE_node_count = data['node_count'][0:num]
        N_IE_layer_count = data['layer_count'][0:num]

        total_node.append(N_IE_node_count[len(N_IE_node_count)-1])

        N_IE_time = time_end - time_start
        N_IE_accumulative_time = 0
        for j in range(0, len(N_IE_time)):
            N_IE_accumulative_time += N_IE_time[j]
        accumulative_time.append(N_IE_accumulative_time)

    print(accumulative_time)
    print(total_node)
    # 创建画板1，显示正态分布的构建时间
    fig = plt.figure(1)  # 如果不传入参数默认画板1
    # 第2步创建画纸，并选择画纸1
    ax1 = plt.subplot(1, 1, 1)
    ax1.plot(sequencelist, accumulative_time, c=colorlist[0], label='CPU Time - Full Node (s)',
             linewidth = 1, marker = '*')
    plt.legend(loc='upper left')
    ax1.set_ylim(1930, 2130)
    # 创建第二坐标轴
    ax2 = ax1.twinx()
    ax2.plot(sequencelist, total_node, c=colorlist[2], label='Total Number of Tree Nodes',
             linewidth = 1, marker = 'o')
    plt.legend(loc='lower right')
    ax2.set_ylim(425, 570)

    ax1.set_xlabel('IE-tree Fan', size = 12)
    ax1.set_ylabel('Accumulation Time of Inserting Resource (s)', size = 12)
    ax2.set_ylabel('Total Number Nodes', size = 12)

    # 显示图像
    plt.show()

if __name__ == '__main__':
    # drawIETreeFanBuildResult()
    # drawDoubleYIETreeFanBuildResult()
    # drawCalculatedRatioOfLeafNode()

    ''''''
    drawBuildResultUseSns() 
    
    drawCalculatedRatioOfLeafNodeUseSns()
    '''
    drawQueryTime500()

    '''
    drawQueryTimeMaxMinMean()

    # drawBuildQueryTreeResult()



    # drawSubscriptionQueryTime()

