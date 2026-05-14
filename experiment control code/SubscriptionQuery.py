from web3 import Web3
import json
import contract7_abi  # E-tree subscription query contract
import contract8_abi  # Quad-tree subscription query contract
import time
import pandas as pd
import os

# 向queryTree中插入订阅查询，用这些数据构建起FBSI树或Quad树
def bulidQueryTree(contractAddress, contractABI, file_path_resource, file_path_result, start, end):
    # 连接Ganache:
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
    # print(w3.isConnected())

    # 获取最新区块号（区块高度）
    print('blockNumber is: %d' % w3.eth.blockNumber)
       
    # 获取订阅查询智能合约接口
    CAKE_BSC_ADDRESS = Web3.toChecksumAddress(contractAddress)
    with open(contractABI, 'r') as f:
        CAKE_BSC_ABI  = json.load(f)

    token_contract = w3.eth.contract(address=CAKE_BSC_ADDRESS, abi=CAKE_BSC_ABI)

    # 设置默认账户，就是发起交易的地址
    w3.eth.defaultAccount = w3.eth.accounts[4]

    '''**************************************'''
    # 从磁盘读取订阅查询数据excel
    file_path = file_path_resource
    metadata = pd.read_excel(file_path, sheet_name='Sheet1')

    # 从磁盘读取结果存放文件，如果不存在就新建
    if(os.path.isfile(file_path_result)==False):
        df=pd.DataFrame()
        df.to_excel(file_path_result)
    result = pd.read_excel(file_path_result, sheet_name='Sheet1')

    queryID = metadata['queryID']
    leftLongitude = metadata['leftLongitude']
    rightLongitude = metadata['rightLongitude']
    downLatitude = metadata['downLatitude']
    topLatitude = metadata['topLatitude']
    endtime = metadata['endtime']
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
        # 取时间
        time_start = time.perf_counter()
        # 铸币
        ''''''
        try:
            tx_hash=token_contract.functions.insertNewSubscribeQuery(int(queryID[i]), int(leftLongitude[i]),
                                                             int(rightLongitude[i]), int(downLatitude[i]),
                                                             int(topLatitude[i]), int(endtime[i]),
                                                             '0xD9300E3Dc7A12a1F1152046a1f15212f6b2ad061',
                                                             keywords[i]).transact()
        except:
            print('添加订阅查询失败，queryID为：{}'.format(i))
        else:
            # 取时间
            time_end = time.perf_counter()
            # 获取gas cost
            tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            gasUsed = tx_receipt['gasUsed']
            # 查节点数量
            node_count = token_contract.functions.getSumQueryTreeNode().call()
            # 写入时间
            result.loc[i, 'queryID'] = i
            result.loc[i, 'time_start'] = time_start
            result.loc[i, 'time_end'] = time_end
            # 写入gas cost
            result.loc[i, 'gasUsed'] = gasUsed
            # 写节点数量
            result.loc[i, 'node_count'] = node_count
            # print(tokenID[serialNo], longitude[serialNo], latitude[serialNo], timestamp[serialNo],keywords[serialNo])
    # 写回excel
    file_path = file_path_result
    pd.DataFrame(result).to_excel(file_path, index=False)

# 在FBSI或Quad的订阅查询树上输入位置-文本数据流，记录订阅查询性能
def resourceStreamForQueryTree(contractAddress, contractABI, file_path_resource, file_path_result, start=0, end=50):
    # 连接Ganache:
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
    # print(w3.isConnected())

    # 获取最新区块号（区块高度）
    print('blockNumber is: %d' % w3.eth.blockNumber)

    # 获取订阅查询合约接口
    CAKE_BSC_ADDRESS = Web3.toChecksumAddress(contractAddress)
    with open(contractABI, 'r') as f:
        CAKE_BSC_ABI  = json.load(f)

    token_contract = w3.eth.contract(address=CAKE_BSC_ADDRESS, abi=CAKE_BSC_ABI)

    # 设置默认账户，就是输入数据流的地址
    w3.eth.defaultAccount = w3.eth.accounts[2]

    '''**************************************'''
    # 从磁盘读取位置-文本数据流excel
    file_path = file_path_resource
    metadata = pd.read_excel(file_path, sheet_name='Sheet1')

    tokenID = metadata['tokenID']
    longitude = metadata['longitude']
    latitude = metadata['latitude']
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

    # 从磁盘读取结果存放文件，如果不存在就新建
    if(os.path.isfile(file_path_result)==False):
        df=pd.DataFrame()
        df.to_excel(file_path_result)
    result = pd.read_excel(file_path_result, sheet_name='Sheet1')

    for i in range(start, end):
        # 取时间
        time_start = time.perf_counter()
        # 铸币
        ''''''
        try:
            tx_hash = token_contract.functions.subscribeQuery(int(longitude[i]), int(latitude[i]), keywords[i],
                                                int(tokenID[i])).transact()
        except:
            print('订阅查询失败，资源流，tokenID为：{}'.format(i))
        #     break
        else:
            # 取时间
            time_end = time.perf_counter()
            # 获取gas cost
            tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            gasUsed = tx_receipt['gasUsed']

            # 写入gas cost
            result.loc[i-start, 'tokenID'] = i
            result.loc[i-start, 'gasUsed'] = gasUsed
            # 写入时间
            result.loc[i-start, 'time_start'] = time_start
            result.loc[i-start, 'time_end'] = time_end

            # print(tokenID[serialNo], longitude[serialNo], latitude[serialNo], timestamp[serialNo],keywords[serialNo])
    # 写回excel
    file_path = file_path_result
    pd.DataFrame(result).to_excel(file_path, index=False)


if __name__ == '__main__':
    ''''''
    query_start = 0
    query_end = 20

    FBSI_Subscription_contract_address = '0xA09044832acD1127F942303c6B92400b29BE9c15'
    Quad_Subscription_contract_address = '0x59c5AAE934c826B0F715A57cC7ff502371cc6616'

    FBSI_Subscription_ABI = 'FBSISubscription.abi'
    Quad_Subscription_ABI = 'QuadSubscription.abi'
   
   # 资源路径和资源插入结果路径,\是转义，因此\\表示\,字符串前的r表示不做转义
    path_prefix = r'C:\订阅查询实验注入数据-2023'
    f_p_normal_SQuery = r'{}\Normal_SubscriptionQuery.xlsx'.format(path_prefix)
    f_p_uniform_SQuery = r'{}\Uniform_SubscriptionQuery.xlsx'.format(path_prefix)
    
    path_prefix = r'C:\订阅查询实验数据-2023'
    f_p_FBSI_build_normal_result = r'{}\Normal_FBSIBuild_Subscription.xlsx'.format(path_prefix)
    f_p_FBSI_build_uniform_result = r'{}\Uniform_FBSIBuild_Subscription.xlsx'.format(path_prefix)
    f_p_Quad_build_normal_result = r'{}\Normal_QuadBuild_Subscription.xlsx'.format(path_prefix)
    f_p_Quad_build_uniform_result = r'{}\Uniform_QuadBuild_Subscription.xlsx'.format(path_prefix)

    # 20个数据一轮，下面定义轮数，最多5轮
    ''''''
    round = 5
    for i in range(0,round):
        start = i*20
        end = (i+1)*20
        # start = 0
        # end = 100

        # 插入订阅查询
        # bulidQueryTree(FBSI_Subscription_contract_address, FBSI_Subscription_ABI, f_p_normal_SQuery, f_p_FBSI_build_normal_result, start, end)
        # bulidQueryTree(FBSI_Subscription_contract_address, FBSI_Subscription_ABI, f_p_uniform_SQuery, f_p_FBSI_build_uniform_result, start, end)
        # bulidQueryTree(Quad_Subscription_contract_address, Quad_Subscription_ABI, f_p_normal_SQuery, f_p_Quad_build_normal_result, start, end)
        bulidQueryTree(Quad_Subscription_contract_address, Quad_Subscription_ABI, f_p_uniform_SQuery, f_p_Quad_build_uniform_result, start, end)

        # 输入位置-文本数据流实验
        # 不同轮次下的查询文件路径
        path_prefix = r'C:\订阅查询实验注入数据-2023'
        f_p_normal_stream = r'{0}\Normal_hitTokenStram.xlsx'.format(path_prefix)
        f_p_uniform_stream = r'{0}\Uniform_hitTokenStram.xlsx'.format(path_prefix)
        # 不同轮次下的查询结果保存路径
        path_prefix = r'C:\订阅查询实验数据-2023'
        f_p_FBSI_SQuery_normal_result = r'{0}\Normal_FBSISubscriptionQuery_{1}.xlsx'.format(path_prefix, end)
        f_p_FBSI_SQuery_uniform_result = r'{0}\Uniform_FBSISubscriptionQuery_{1}.xlsx'.format(path_prefix, end)

        f_p_Quad_SQuery_normal_result = r'{0}\Normal_QuadSubscriptionQuery_{1}.xlsx'.format(path_prefix, end)
        f_p_Quad_SQuery_uniform_result = r'{0}\Uniform_QuadSubscriptionQuery_{1}.xlsx'.format(path_prefix, end)

        # resourceStreamForQueryTree(FBSI_Subscription_contract_address, FBSI_Subscription_ABI, f_p_normal_stream, f_p_FBSI_SQuery_normal_result, start, end)
        # resourceStreamForQueryTree(FBSI_Subscription_contract_address, FBSI_Subscription_ABI, f_p_uniform_stream, f_p_FBSI_SQuery_uniform_result, start, end)
        # resourceStreamForQueryTree(Quad_Subscription_contract_address, Quad_Subscription_ABI, f_p_normal_stream, f_p_Quad_SQuery_normal_result, start, end)
        resourceStreamForQueryTree(Quad_Subscription_contract_address, Quad_Subscription_ABI, f_p_uniform_stream, f_p_Quad_SQuery_uniform_result, start, end)