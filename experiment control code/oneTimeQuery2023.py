
from web3 import Web3
import json
import contract5_abi  # IE-tree结构，单次查询，合约无倒排文件辅助查询
import contract6_abi  # Quad-tree结构，单次查询
import time
import pandas as pd
import os


def buildTree(contractAddress, contractABI, file_path_resource, file_path_result, start, end):
    # 连接Ganache:
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
    # print(w3.isConnected())

    # 获取最新区块号（区块高度）
    print('blockNumber is: %d' % w3.eth.blockNumber)

    # 获取合约接口
    CAKE_BSC_ADDRESS = Web3.toChecksumAddress(contractAddress)
    with open(contractABI, 'r') as f:
        CAKE_BSC_ABI  = json.load(f)

    token_contract = w3.eth.contract(address=CAKE_BSC_ADDRESS, abi=CAKE_BSC_ABI)

    # 设置默认账户，就是发起交易的地址
    w3.eth.defaultAccount = w3.eth.accounts[4]

    '''**************************************'''
    # 从磁盘读取NFT元数据excel
    metadata = pd.read_excel(file_path_resource, sheet_name='Sheet1')

    # 从磁盘读取结果存放文件，如果不存在就新建
    if(os.path.isfile(file_path_result)==False):
        df=pd.DataFrame()
        df.to_excel(file_path_result)
    rusult = pd.read_excel(file_path_result, sheet_name='Sheet1')

    '''
    print(metadata.describe())

                tokenID     Longitude      Latitude  timestamp
    count  100000.000000  1.000000e+05  1.000000e+05   100000.0
    mean    49999.500000  4.995876e+11  4.001268e+11     1000.0
    std     28867.657797  8.039563e+10  3.997395e+10        0.0
    min         0.000000  1.335829e+11  2.322546e+11     1000.0
    25%     24999.750000  4.453677e+11  3.731116e+11     1000.0
    50%     49999.500000  4.991047e+11  4.001391e+11     1000.0
    75%     74999.250000  5.541506e+11  4.268809e+11     1000.0
    max     99999.000000  8.257314e+11  5.711613e+11     1000.0
    '''

    tokenID = metadata['tokenID']
    longitude = metadata['Longitude']
    latitude = metadata['Latitude']
    timestamp = metadata['timestamp']
    original_keywords = metadata['keywords']
    keywords = []

    # 修正keywords类型错误：从excel中读取keywords是str,但实际需要是list
    for i in range(0, len(original_keywords)):
        temp_keywords = original_keywords[i].replace('[', '')
        temp_keywords = temp_keywords.replace(']', '')
        temp_keywords = temp_keywords.replace('\'', '')
        temp_keywords = temp_keywords.replace(' ', '')
        temp_keywords = temp_keywords.split(sep=',')
        keywords.append(temp_keywords)

    for i in range(start, end):
        # 取当前系统时间
        time_start = time.perf_counter()
        # 铸币
        ''''''
        try:
            tx_hash = token_contract.functions.mint_(int(tokenID[i]), int(longitude[i]), int(latitude[i]),
                                           int(timestamp[i]), '0xD9300E3Dc7A12a1F1152046a1f15212f6b2ad061',
                                           'uri', 1, keywords[i]).transact()
        except:
            print('铸币失败，tokenID为：{}'.format(i))
        else:
            # 取当前系统时间
            time_end = time.perf_counter()
            # 获取gas cost
            tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            gasUsed = tx_receipt['gasUsed']
            # 查节点数量和层数
            node_count = token_contract.functions.getSumTokenTreeNode().call()
            layer_count = token_contract.functions.getTokenTreeHigh().call()

            # 写入时间
            rusult.loc[i, 'tokenID'] = tokenID[i]
            rusult.loc[i, 'time_start'] = time_start
            rusult.loc[i, 'time_end'] = time_end
            # 写入gas cost
            rusult.loc[i, 'gasUsed'] = gasUsed
            # 写节点数量和层数
            rusult.loc[i, 'node_count'] = node_count
            rusult.loc[i, 'layer_count'] = layer_count

    # 写回excel
    pd.DataFrame(rusult).to_excel(file_path_result, index=False)


def queryTree(contractAddress, contractABI, file_path_resource, file_path_result):
    # 连接Ganache:
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
    # print(w3.isConnected())

    # 获取最新区块号（区块高度）
    print('blockNumber is: %d' % w3.eth.blockNumber)

    # 获取合约接口
    CAKE_BSC_ADDRESS = Web3.toChecksumAddress(contractAddress)
    with open(contractABI, 'r') as f:
        CAKE_BSC_ABI  = json.load(f)

    token_contract = w3.eth.contract(address=CAKE_BSC_ADDRESS, abi=CAKE_BSC_ABI)

    # 设置默认账户，就是发起交易的地址
    w3.eth.defaultAccount = w3.eth.accounts[2]

    # 从磁盘读取查询条件excel
    queryCondition = pd.read_excel(file_path_resource, sheet_name='Sheet1')

    leftLon = queryCondition['leftLongitude']
    rightLon = queryCondition['rightLongitude']
    bottomLat = queryCondition['bottomLatitude']
    topLat = queryCondition['topLatitude']
    original_keywords = queryCondition['queryKeywords']
    queryNo = queryCondition['queryNo']

    queryKeywords = []

    # 修正keywords类型错误：从excel中读取keywords是str,但实际需要是list
    for i in range(0, len(original_keywords)):
        temp_keywords = original_keywords[i].replace('[', '')
        temp_keywords = temp_keywords.replace(']', '')
        temp_keywords = temp_keywords.replace('\'', '')
        temp_keywords = temp_keywords.replace(' ', '')
        temp_keywords = temp_keywords.split(sep=',')
        queryKeywords.append(temp_keywords)

    for i in range(0, len(queryNo)):
        # 取当前系统时间
        time_start = time.perf_counter()
        # 查询交易
        try:
            tx_hash = token_contract.functions.onceQuery(int(leftLon[i]), int(rightLon[i]), int(bottomLat[i]),
                                           int(topLat[i]), queryKeywords[i], int(queryNo[i]), False).transact()
        except:
            print('查询失败，queryID为：{}'.format(i))
        else:
            # 取当前系统时间
            time_end = time.perf_counter()
            # 获取gas cost
            tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            gasUsed = tx_receipt['gasUsed']

            # 写入gas cost
            queryCondition.loc[i, 'gasUsed'] = gasUsed
            # 写入时间
            queryCondition.loc[i, 'time_start'] = time_start
            queryCondition.loc[i, 'time_end'] = time_end

    # 写回excel
    pd.DataFrame(queryCondition).to_excel(file_path_result, index=False)


if __name__ == '__main__':
    E_contract_address = '0xcE91d3Ee83758C58C510861E65E7780e842252B1'

    FBSI_contract_address = '0xA54D0E1531895ed8f2B5c4A26f11C669C7c5517F'

    Quad_contract_address = '0xB968D8c40e5B62a904B953b1eC0E4d0276BEc425'

    E_contract_ABI = 'ETree.abi' # 未进行数据长度优化的FBSI结构，即老版E-tree
    FBSI_contract_ABI = 'FBSIQuery.abi'
    Quad_contract_ABI = 'QuadQuery.abi'
    # 资源路径和资源插入结果路径,\是转义，因此\\表示\,字符串前的r表示不做转义
    path_prefix = r'C:\实验注入数据2'
    file_path_normal_resource = r'{}\Normally_distribute_resource_data.xlsx'.format(path_prefix)
    file_path_uniform_resource = r'{}\Uniform_distribute_resource_data.xlsx'.format(path_prefix)
    path_prefix = r'C:\实验数据'
    file_path_E_build_normal_result = r'{}\Normally_ETreeBuild_test.xlsx'.format(path_prefix)
    file_path_E_build_uniform_result = r'{}\Uniform_ETreeBuild_test.xlsx'.format(path_prefix)

    file_path_FBSI_build_normal_result = r'{}\Normally_FBSIBuild_test.xlsx'.format(path_prefix)
    file_path_FBSI_build_uniform_result = r'{}\Uniform_FBSIBuild_test.xlsx'.format(path_prefix)

    file_path_Quad_build_normal_result = r'{}\Normally_QuadTreeBuild_test.xlsx'.format(path_prefix)
    file_path_Quad_build_uniform_result = r'{}\Uniform_QuadTreeBuild_test.xlsx'.format(path_prefix)   

    # 500个数据一轮，下面定义轮数，最多5 轮
    ''''''
    round = 15
    for i in range(0,round):
        start = i*20
        end = (i+1)*20
        # 插入资源
        # buildTree(E_contract_address, E_contract_ABI, file_path_normal_resource, file_path_E_build_normal_result, start, end)
        # buildTree(E_contract_address, E_contract_ABI, file_path_uniform_resource, file_path_E_build_uniform_result, start, end)
        
        # buildTree(FBSI_contract_address, FBSI_contract_ABI, file_path_normal_resource, file_path_FBSI_build_normal_result, start, end)
        # buildTree(FBSI_contract_address, FBSI_contract_ABI, file_path_uniform_resource, file_path_FBSI_build_uniform_result, start, end)
        
        # buildTree(Quad_contract_address, Quad_contract_ABI, file_path_normal_resource, file_path_Quad_build_normal_result, start, end)
        buildTree(Quad_contract_address, Quad_contract_ABI, file_path_uniform_resource, file_path_Quad_build_uniform_result, start, end)
        
        # 查询(按范围比)
        for ratio in range(1,4):
            # 不同轮次下的查询文件路径
            rangeRatio = ratio/100
            path_prefix = r'C:\实验注入数据2\查询条件(经度划分)'
            file_path_normal_query = r'{0}\Normally_distribute_query_conditions_from{1}_{2}.xlsx'.format(path_prefix, end, rangeRatio)
            file_path_uniform_query = r'{0}\Uniform_distribute_query_conditions_from{1}_{2}.xlsx'.format(path_prefix, end, rangeRatio)
            # 不同轮次下的查询结果保存路径
            path_prefix = r'C:\实验数据'
            file_path_E_query_normal_result = r'{0}\Normally_ETreeQuery_{1}_{2}.xlsx'.format(path_prefix, end, rangeRatio)
            file_path_E_query_uniform_result = r'{0}\Uniform_ETreeQuery_{1}_{2}.xlsx'.format(path_prefix, end, rangeRatio)

            file_path_FBSI_query_normal_result = r'{0}\Normally_FBSIQuery_{1}_{2}.xlsx'.format(path_prefix, end, rangeRatio)
            file_path_FBSI_query_uniform_result = r'{0}\Uniform_FBSIQuery_{1}_{2}.xlsx'.format(path_prefix, end, rangeRatio)

            file_path_Quad_query_normal_result = r'{0}\Normally_QuadTreeQuery_{1}_{2}.xlsx'.format(path_prefix, end, rangeRatio)
            file_path_Quad_query_uniform_result = r'{0}\Uniform_QuadTreeQuery_{1}_{2}.xlsx'.format(path_prefix, end, rangeRatio)

            # queryTree(E_contract_address, E_contract_ABI, file_path_normal_query, file_path_E_query_normal_result)
            # queryTree(E_contract_address, E_contract_ABI, file_path_uniform_query, file_path_E_query_uniform_result)

            # queryTree(FBSI_contract_address, FBSI_contract_ABI, file_path_normal_query, file_path_FBSI_query_normal_result)
            # queryTree(FBSI_contract_address, FBSI_contract_ABI, file_path_uniform_query, file_path_FBSI_query_uniform_result)

            # queryTree(Quad_contract_address, Quad_contract_ABI, file_path_normal_query, file_path_Quad_query_normal_result)
            # queryTree(Quad_contract_address, Quad_contract_ABI, file_path_uniform_query, file_path_Quad_query_uniform_result)
        
        # 查询（随机）
        # 不同轮次下的查询文件路径
        path_prefix = r'C:\实验注入数据2'
        file_path_normal_query = r'{0}\Normally_distribute_query_conditions_from{1}.xlsx'.format(path_prefix, end)
        file_path_uniform_query = r'{0}\Uniform_distribute_query_conditions_from{1}.xlsx'.format(path_prefix, end)
        # 不同轮次下的查询结果保存路径
        path_prefix = r'C:\实验数据'
        file_path_E_query_normal_result = r'{0}\Normally_ETreeQuery_{1}.xlsx'.format(path_prefix, end)
        file_path_E_query_uniform_result = r'{0}\Uniform_ETreeQuery_{1}.xlsx'.format(path_prefix, end)

        file_path_FBSI_query_normal_result = r'{0}\Normally_FBSIQuery_{1}.xlsx'.format(path_prefix, end)
        file_path_FBSI_query_uniform_result = r'{0}\Uniform_FBSIQuery_{1}.xlsx'.format(path_prefix, end)

        file_path_Quad_query_normal_result = r'{0}\Normally_QuadTreeQuery_{1}.xlsx'.format(path_prefix, end)
        file_path_Quad_query_uniform_result = r'{0}\Uniform_QuadTreeQuery_{1}.xlsx'.format(path_prefix, end)

        # queryTree(E_contract_address, E_contract_ABI, file_path_normal_query, file_path_E_query_normal_result)
        # queryTree(E_contract_address, E_contract_ABI, file_path_uniform_query, file_path_E_query_uniform_result)

        # queryTree(FBSI_contract_address, FBSI_contract_ABI, file_path_normal_query, file_path_FBSI_query_normal_result)
        # queryTree(FBSI_contract_address, FBSI_contract_ABI, file_path_uniform_query, file_path_FBSI_query_uniform_result)

        # queryTree(Quad_contract_address, Quad_contract_ABI, file_path_normal_query, file_path_Quad_query_normal_result)
        queryTree(Quad_contract_address, Quad_contract_ABI, file_path_uniform_query, file_path_Quad_query_uniform_result)
    
