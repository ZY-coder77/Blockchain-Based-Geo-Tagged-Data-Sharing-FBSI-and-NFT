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


# 使用seaborn库绘制构建树形结构中节点分裂时间直方图（含概率密度分布曲线）和节点-资源数关系图
def drawBuildResultUseSns():
    startnum = 0
    endnum = 2500
    node_capacity = 10

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
    # 创建画板
    frontsize = 20
    fig1 = plt.figure(1)
    ax1 = fig1.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.14, right=0.96, top=0.99, bottom=0.16)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    fig2 = plt.figure(2)
    ax2 = fig2.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.14, right=0.96, top=0.99, bottom=0.16)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    subplot = [ax1, ax2]

    fig3 = plt.figure(3)
    ax3 = fig3.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.19, right=0.96, top=0.99, bottom=0.15)
    plt.xticks(fontsize=frontsize)
    plt.yticks(fontsize=frontsize)
    fig4 = plt.figure(4)
    ax4 = fig4.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.19, right=0.96, top=0.99, bottom=0.15)
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
        layer_count = data['layer_count'][startnum:endnum]

        temptime = time_end - time_start
        accumulative_time = time_end - time_start
        # 过滤time中小于1.5秒的数据，主要观察其中的分裂时间
        temptime = temptime.tolist()
        time = []
        for k in range(0, len(temptime)):
            if temptime[k] >= 1.5:
                time.append(temptime[k])

        # 绘制节点分裂时间直方图  hatch=hatch[int(i%2)], color=color[int(i % 2)],
        # sns.histplot(time, color=colorlist[int(i % 2)], bins=20, binrange=(1.5,5.0), stat='probability', kde=True, alpha=0.5, legend=True, ax=subplot[int(i / 2)])
        sns.histplot(time, bins=11, binrange=(1.5, 5.0), stat='density', kde=False, alpha=alpha[int(i%2)], ax=subplot[int(i/2)])
        # sns.kdeplot(time, linewidth=2.5, ax=subplot[int(i / 2)])
        # subplot[int(i / 2)].lines[-1].set_linestyle('--')  # stat='density'   stat='percent' line_kws={'linestyle': '--'},
        print("平均分裂时间：", np.mean(time))


        # 删除资源数量增加但节点不增的数据
        tokenID = tokenID.tolist()
        node_count = node_count.tolist()
        j = 1
        while j < len(tokenID):
            if node_count[j] > 480:
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
        subplot2[int(i / 2)].plot(node_count, tokenID, color=colorlist[int(i % 2)], alpha=0.8)


    # fig1.subplots_adjust(hspace=0.5)
    ax1.set_xlabel('Time for Splitting a Node (s)(Normal)', size=frontsize)
    ax1.set_ylabel('Proportion of Split Nodes (%)', size=frontsize)
    ax1.set_xlim(1.0, 5.0)
    ax1.set_yticks(np.linspace(0, 1.43057, 6), range(0, 26, 5))
    ax1.set_ylim(0.0, 1.5)
    ax1.legend(legend, loc='upper left', prop=font1)

    ax2.set_xlabel('Time for Splitting a Node (s)(Uniform)', size=frontsize)
    ax2.set_ylabel('Proportion of Split Nodes (%)', size=frontsize)
    ax2.set_xlim(1.0, 5.0)
    ax2.set_yticks(np.linspace(0, 1.4278, 6), range(0, 26, 5))
    ax2.set_ylim(0.0, 1.5)
    ax2.legend(legend, loc='upper left', prop=font1)

    ax3.fill_between(node_count_list[0], tokenID_list[0], 0,  # 上限，下限
                     facecolor=colorlist[3],  # 填充颜色
                     alpha=0.2)  # 透明度
    ax3.fill_between(node_count_list[1], tokenID_list[1], 0,  # 上限，下限
                     facecolor=colorlist[2],  # 填充颜色
                     alpha=0.2)  # 透明度
    ax3.set_xlabel('Number of Nodes (Normal)', size=frontsize)
    ax3.set_ylabel('NFT Objects', size=frontsize) # 'Number of Resources'
    # ax3.set_xlim(1.4, 4.7)
    # ax3.set_ylim(0.0, 0.26)
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
    # ax4.set_xlim(1.4, 4.7)
    # ax4.set_ylim(0.0, 0.26)
    ax4.legend(legend, prop=font1)
    print('数据容量-uniform-FBSI：', tokenID_list[2][len(tokenID_list[2]) - 1])
    print('数据容量-uniform-quad：', tokenID_list[3][len(tokenID_list[3]) - 1])

    # 显示图像
    plt.show()


# 使用seaborn库绘制叶节点容量使用率密度分布图
def drawCalculatedRatioOfLeafNodeUseSns():

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
    file_path = r'C:\WorkFile\服务器实验数据\叶节点负载统计实验\Resource_number_on_leaf_node_IE_Normal.xlsx'
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    # sns.histplot(data['NormallyIETree'], bins=11, binrange=(0, 11), stat='density', hatch='xx', kde=False, alpha=0.7, ax=ax1)
    sns.kdeplot(data['NormallyIETree'], linewidth=2.5, ax=ax1)# color=color[0],
    # ax1.lines[-1].set_linestyle('--')  # stat='density'   stat='percent'  line_kws={'linestyle': '--'}
    print('alpha FBSI normal:', np.mean(data['NormallyIETree']))

    file_path = r'C:\WorkFile\服务器实验数据\叶节点负载统计实验\Resource_number_on_leaf_node_Quad_Normal.xlsx'
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    # sns.histplot(data['NormallyQuadTree'], bins=11, binrange=(0, 11), stat='density', hatch='/', kde=False, alpha=0.2, ax=ax1)
    sns.kdeplot(data['NormallyQuadTree'], linewidth=2.5, ax=ax1)# color=color[1],
    # ax1.lines[-1].set_linestyle('--')  # stat='density'   stat='percent'  line_kws={'linestyle': '--'}

    ax1.legend(legend, loc='upper left', prop=font2)
    ax1.set_xlabel('Resource Capacity Ratio (%) (Normal)', font1)
    ax1.set_ylabel('Proportion of Leaf Nodes (%)', font1)
    ax1.set_xticks(np.linspace(0.5, 10.5, 6), range(0, 110, 20), size=frontsize)
    ax1.set_yticks(np.linspace(0, 0.30, 7), range(0, 31, 5), size=frontsize)
    ax1.set_xlim(-0.5, 11.5)
    ax1.set_ylim(0, 0.28)
    # plt.show()
    print('alpha-quad normal:', np.mean(data['NormallyQuadTree']))

    file_path = r'C:\WorkFile\服务器实验数据\叶节点负载统计实验\Resource_number_on_leaf_node_IE_Uniform.xlsx'
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    # sns.histplot(data['UniformIETree'], bins=11, binrange=(0, 11), stat='density', hatch='xx', kde=False, alpha=0.7, ax=ax2)# hatch='xx',
    sns.kdeplot(data['UniformIETree'], linewidth=2.5, ax=ax2)# color=color[0],
    # ax2.lines[-1].set_linestyle('--')  # stat='density'   stat='percent'  line_kws={'linestyle': '--'}
    print('alpha FBSI uniform :', np.mean(data['UniformIETree']))

    file_path = r'C:\WorkFile\服务器实验数据\叶节点负载统计实验\Resource_number_on_leaf_node_Quad_Uniform.xlsx'
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    # sns.histplot(data['UniformQuadTree'], bins=11, binrange=(0, 11), stat='density', hatch='/', kde=False, alpha=0.2, ax=ax2)# hatch='/',
    sns.kdeplot(data['UniformQuadTree'], linewidth=2.5,  ax=ax2)# color=color[1],
    # ax2.lines[-1].set_linestyle('--')  # stat='density'   stat='percent'  line_kws={'linestyle': '--'}
    print('alpha quad uniform :', np.mean(data['UniformQuadTree']))

    ax2.legend(legend, loc='upper left', prop=font2)
    ax2.set_xlabel('Resource Capacity Ratio (%) (Uniform)', font1)
    ax2.set_ylabel('Proportion of Leaf Nodes (%)', font1)
    ax2.set_xticks(np.linspace(0.5, 10.5, 11), range(0, 110, 10), size=frontsize)
    ax2.set_yticks(np.linspace(0, 0.25, 6), range(0, 26, 5), size=frontsize)
    ax2.set_xlim(-0.5, 11.5)
    ax2.set_ylim(0, 0.27)
    plt.show()


# 分批注入2500个资源数据，每500个时执行一组（50）个查询，E-tree每组取最小值，Quad-tree每组取最大值，绘制线图
def drawQueryTimeMaxMinMean():
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

    print('平均查询时间（FBSI normal）：', np.mean(E_time[0]))
    print('平均查询时间（quad normal）：', np.mean(Q_time[0]))
    print('平均查询时间（FBSI uniform）：', np.mean(E_time[1]))
    print('平均查询时间（quad uniform）：', np.mean(Q_time[1]))

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
    
    drawBuildResultUseSns()
    '''


    drawCalculatedRatioOfLeafNodeUseSns()'''
    '''
    drawQueryTimeMaxMinMean()
    '''
    # drawBuildQueryTreeResult()

    # drawSubscriptionQueryTime()

