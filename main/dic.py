import json

order_dic = {
    '#4a':
        {
            'id': 1,
            'param_count': 1,
            'system': '4a',
            'actual_order': '#4a_login_clone',
            1: {
                'name': '无用参数',
                'property': {'type': int},
            },
        },
    '#sms':
        {
            'id': 2,
            'param_count': 2,
            'system': '4a',
            'actual_order': '#4a_sms',
            1: {
                'name': '4A登陆验证码',
                'property': {'type': int, 'length': 6},
            },
            2: {
                'name': 'loginForm码',
                'property': {'type': int, 'length': [19, 20]},
            }
        },
    '#iot':
        {
            'id': 11,
            'param_count': 1,
            'system': '4a',
            'actual_order': '#4a_iot',
            1: {
                'name': '登陆iot',
                'property': {'type': str},
            }
        },

    # 1001~1100 分配为查询用途
    '#puk':
        {
            'id': 1001,
            'param_count': 1,
            'system': 'iot',
            'actual_order': '#iot_puk',
            'whitelist': ['深**徕纳智能科技有限公司', '深**禾锐通信有限公司','统**信(苏州)有限公司广州分公司', '统**信（苏州）有限公司广州分公司'],
            1: {
                'name': '物联网号码',
                'property': {'type': int, 'length': [13,11], 'first_num': '1'},
                }
        },
    '#查实名':
        {
            'id': 1002,
            'param_count': 1,
            'system': 'iot',
            'actual_order': '#iot_puk',
            1: {
                'name': '物联网号码',
                'property': {'type': int, 'length': [13,11], 'first_num': '1'}
            }

        },
    '#查状态':
        {
            'id': 1003,
            'param_count': 1,
            'system': 'iot',
            'actual_order': '#iot_status',
            1: {
                'name': '物联网号码',
                'property': {'type': int, 'length': [13,11], 'first_num': '1'}
            }

        },
    '#查余额':
        {
            'id': 1003,
            'param_count': 1,
            'system': 'iot',
            'actual_order': '#iot_outstanding_fees',
            1: {
                'name': '物联网号码',
                'property': {'type': int, 'length': [13,11], 'first_num': '1'}
            }

        },
    '#查欠费':
        {
            'id': 1003,
            'param_count': 1,
            'system': 'iot',
            'actual_order': '#iot_outstanding_fees',
            1: {
                'name': '物联网号码',
                'property': {'type': int, 'length': [13,11], 'first_num': '1'}
            }

        },

    # 4001~4500 分配为特定客户使用
    '#徕纳500':
        {
            'id': 4001,
            'param_count': 1,
            'system': 'iot',
            'actual_order': '#laina500',
            # 1: {
            #     'name': '10或者100流量池',
            #     'property': {'content': [10,100]}
            # },
            1: {
                'name': '物联网号码',
                'property': {'type': int, 'length': 11, 'first_num': '1'}
            }
        },
    '#申请开机':
        {
            'id': 4002,
            'param_count': 1,
            'system': 'iot',
            'actual_order': '#open&stop_shenqing',
            1: {
                'name': '物联网号码',
                'property': {'type': int, 'length': [11,13], 'first_num': '1'}
            }
        }
    }


