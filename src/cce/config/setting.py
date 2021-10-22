from rich import print

CONFIG_TXT = {
    'ENABLE_QCN': '1',
    'USE_DYNAMIC_PFC_THRESHOLD': '0',
    'PACKET_LEVEL_ECMP': '0',
    'FLOW_LEVEL_ECMP': '1',
    'PAUSE_TIME': '5',
    'PACKET_PAYLOAD_SIZE': '1000',
    'TOPOLOGY_FILE': 'mix/topology.txt',
    'FLOW_FILE': 'mix/flow.txt',
    'TCP_FLOW_FILE': 'mix/flow_tcp_0.txt',
    'TRACE_FILE': 'mix/trace.txt',
    'TRACE_OUTPUT_FILE': 'mix/mix.tr',
    'SEND_IN_CHUNKS': '1',
    'APP_START_TIME': '0.0',
    'APP_STOP_TIME': '2.0',
    'SIMULATOR_STOP_TIME': '2.01',
    'CNP_INTERVAL': '50',
    'ALPHA_RESUME_INTERVAL': '55',
    'NP_SAMPLING_INTERVAL': '0',
    'CLAMP_TARGET_RATE': '1',
    'CLAMP_TARGET_RATE_AFTER_TIMER': '0',
    'RP_TIMER': '60',
    'BYTE_COUNTER': '10000000',
    'DCTCP_GAIN': '0.00390625',
    'KMAX': '50',
    'KMIN': '5',
    'PMAX': '0.01',
    'FAST_RECOVERY_TIMES': '5',
    'RATE_AI': '40Mb/s',
    'RATE_HAI': '200Mb/s',
    'PFC': '100',
    'ERROR_RATE_PER_LINK': '0.0000',
    'L2_CHUNK_SIZE': '4000',
    'L2_WAIT_FOR_ACK': '0',
    'L2_ACK_INTERVAL': '256',
    'L2_BACK_TO_ZERO': '0'
}


# def read_config()->dict[str, str]:
#     file = '../static/config.txt'
#     conf = {}
#     with open(file, 'r') as f:
#         while True:
#             line = f.readline()
#             if line == '': break
#             line = line.strip().split(' ')
#             if len(line) > 1: conf[line[0]] = line[1]
#     return conf

def set_config(settings: dict[str, str]) -> str:
    print(settings)
    for k, v in settings.items(): CONFIG_TXT[k] = v
    res = []
    for k, v in CONFIG_TXT.items(): res.append(f'{k} {v}\n')
    return ''.join(res)
