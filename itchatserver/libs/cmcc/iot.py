
# -*-encoding:utf-8-*-
import random
from bs4 import BeautifulSoup
import  logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

header = {
    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET4.0C; .NET4.0E)',
    'Accept': '*/*', 'Accept-Language': 'zh-CN', 'Accept-Encoding': 'gzip, deflate'}
header2 = {
    'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; WOW64; Trident/6.0; SE 2.X MetaSr 1.0)',
    'Accept': '*/*', 'Accept-Language': 'zh-cn', 'Accept-Encoding': 'gzip, deflate',
    'X-Requested-With': 'XMLHttpRequest'}


def test_alive(r, proxies, auth):
    try:
        iot_outstanding_fees_1(r, '17228107947', proxies, auth)
        return 'alive'
    except Exception as e:
        logger.error(e)
        return 'not alive'


def iot_outstanding_fees_1(_r, phone_num, _proxies, _auth):
    _random = '0.'+str(random.randint(100000000000000,999999999999999))+str(random.randint(1,9))
    url = 'http://10.253.61.8/ngcustcare/chargesrv/common/qryRelateSubs.action?servNumber=' + phone_num + '&isSupportGrp=undefined&random='+_random
    s = _r.get(url, headers=header, auth=_auth, proxies=_proxies)
    soup = BeautifulSoup(s.text, 'lxml')
    s = soup.select('.table_list02 tr[name = "subscriber_tr"] input[name="status"]')
    _len = s.__len__()
    _range = range(_len)
    for _i in _range:
        if s[_i].attrs['value'] != 'US99':
            return soup.select('.table_list02 tr[name = "subscriber_tr"] input[name="subsId"]')[_i].attrs['value']
        else:
            result = soup.select('.table_list02 tr[name = "subscriber_tr"] input[name="subsId"]')[_i].attrs['value']
    return result
    # 返回欠费查询的subsid


def iot_outstanding_fees_2(_r, _sub_sid, phone_num, _proxies, _auth):
    url = 'http://10.253.61.8/ngcustcare/chargesrv/accountInfoQry/balanceQry/query.action'
    param = {'subsId': _sub_sid, 'searchType': 'servNumber', 'searchNumber': phone_num, 'balanceType': 'CanUse'}
    s = _r.post(url, data=param, auth=_auth, proxies=_proxies)
    soup = BeautifulSoup(s.text, 'lxml')
    _list = soup.select('.table_list03')[1].select('td')
    _result = ''
    for _i in _list:
        _a = ''.join(_i.text).split()
        if len(_a) > 0:
            _result = _result + '\n'+_a[0]
    return _result


def iot_status(_r, phone_num, _proxies, _auth):
    header1 = {
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET4.0C; .NET4.0E)',
        'Accept': '*/*', 'Accept-Language': 'zh-CN', 'Accept-Encoding': 'gzip, deflate',
        'x-requested-with': 'XMLHttpRequest', 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Content-Length': '20'}
    _result_step1 = iot_phone_query_base_setp1(_r, phone_num, _proxies, _auth)
    _result_step2 = iot_phone_query_base_setp2(_r, _result_step1, phone_num, _proxies, _auth)
    url = 'http://10.253.61.8/nguniteview/layoutAction.do?method=showView&ownerType=1&viewId=200'
    _param = {'width': '1098', 'height': '14'}
    s = _r.post(url, data=_param, headers=header1, auth=_auth, proxies=_proxies)
    soup = BeautifulSoup(s.text, 'lxml')
    _result_status = soup.select('.fv_tb_tr')[0].select('td')[3].text
    if _result_status != '停机':
        return _result_status
    else:
        _result_stopKeyValue = BeautifulSoup(_result_step1.text, 'lxml').select('input[name="stopKeyValue"]')[0].attrs['value']
        return _result_stopKeyValue


def cn_cookies1(r,cookies, phone_num):
    cookies = dict()
    for i in r.cookies.get_dict('10.253.61.8'):
        cookies[i] = r.cookies.get(i, '', '10.253.61.8')
        cookies['bsacKF'] = 'NGCRM_BOSS'
        cookies['com.huawei.boss.CONTACTID'] = 'undefined'
        cookies['com.huawei.boss.CURRENT_MENUID'] = '100110121062'
        cookies['com.huawei.boss.CURRENT_TAB'] = 'BOSS%5E' + phone_num + '%5E100110121062%7E' + phone_num
        cookies['com.huawei.boss.CURRENT_USER'] = phone_num
        cookies['MACAddr'] = 'null'
        cookies['sDNSName'] = '3B8MB8'
        return cookies


# 号码综合查询_setp1
def iot_phone_query_base_setp1(r, phone_num, _proxies, _auth, _type=None):
    def cn_cookies(cookies_temp):
        cookies = dict()
        for i in r.cookies.get_dict('10.253.61.8'):
            cookies[i] = r.cookies.get(i, '', '10.253.61.8')
        cookies['bsacKF'] = 'NGCRM_BOSS'
        cookies['com.huawei.boss.CONTACTID'] = 'null'
        cookies['com.huawei.boss.CURRENT_MENUID'] = 'null'
        cookies['com.huawei.boss.CURRENT_TAB'] = 'cvalida'
        cookies['com.huawei.boss.CURRENT_USER'] = 'com.huawei.boss.NO_CURRENT_USER'
        return cookies

    cookies1 = cn_cookies(r.cookies)
    url = 'http://10.253.61.8/ngcustcare/custlogin/qryCustInfo.action'
    param = {'method': 'qryCustInfo', 'servNumber': phone_num, 'authCheckMode': 'AuthCheckZ', 'verifyCode': '',
             'pswd': '', 'certType': 'IdCard', 'certID': '', 'rndPswd': '', 'custType': 'PersonCustomer',
             'domainType': 'null', 'isCert2G': '', 'ONLYLOGIN': 'onlyLogin', 'withoutPassValidate': 'true',
             'isUseReadIdCardWithTwo': '0'}
    s = r.post(url, cookies=cookies1, data=param, headers=header2, auth=_auth, proxies=_proxies)
    cn_cookies = cn_cookies1(r, r.cookies, phone_num)
    url2 = 'http://10.253.61.8/ngcustcare/uniteview/uviewtwo/uvDisper.action?currentTabID=BOSS^' + phone_num + '^100110121062~' + phone_num
    s2 = r.get(url2, cookies=cn_cookies, headers=header2, auth=_auth, proxies=_proxies)

    if _type == 'name':
        _soup = BeautifulSoup(s2.text, 'lxml')
        _name =_soup.select('.panel input[name="ccm_EntityName"]')[0].attrs['value']
        return s2,_name
    else:
        return s2


# 号码综合查询_setp2
def iot_phone_query_base_setp2(r, s2, phone_num, _proxies, _auth):
    def cn_soup(temp):
        a = soup.find(attrs={"name": temp}).attrs['value']
        return a
    soup = BeautifulSoup(s2.text, 'lxml')
    cn_cookies3 = cn_cookies1(r, r.cookies, phone_num)
    url3 = 'http://10.253.61.8/nguniteview/bossviewhome.jsp'
    param3 = {'ccm_ObjectID': '', 'ccm_RandomNum': '', 'ccdirect': soup.find(attrs={"name": "ccdirect"}).attrs['value'],
              'ccm_EntityID': soup.find(attrs={"name": "ccm_EntityID"}).attrs['value'],
              'ccm_EntityName': soup.find(attrs={"name": "ccm_EntityName"}).attrs['value'],
              'ccm_CreateDate': soup.find(attrs={"name": "ccm_CreateDate"}).attrs['value'],
              'ccm_Status': soup.find(attrs={"name": "ccm_Status"}).attrs['value'],
              'ccm_StatusDate': soup.find(attrs={"name": "ccm_StatusDate"}).attrs['value'],
              'ccm_EditStatus': soup.find(attrs={"name": "ccm_EditStatus"}).attrs['value'], 'ccm_Region': '200',
              'ccm_ShortName': '', 'ccm_Password': soup.find(attrs={"name": "ccm_Password"}).attrs['value'],
              'ccm_CustType': 'PersonCustomer', 'ccm_VipType': soup.find(attrs={"name": "ccm_VipType"}).attrs['value'],
              'ccm_Foreigner': soup.find(attrs={"name": "ccm_Foreigner"}).attrs['value'],
              'ccm_CustClass1': soup.find(attrs={"name": "ccm_CustClass1"}).attrs['value'],
              'ccm_CustClass2': soup.find(attrs={"name": "ccm_CustClass2"}).attrs['value'],
              'ccm_National': soup.find(attrs={"name": "ccm_National"}).attrs['value'], 'ccm_Address': '********',
              'ccm_CertID': soup.find(attrs={"name": "ccm_CertID"}).attrs['value'],
              'ccm_CertType': soup.find(attrs={"name": "ccm_CertType"}).attrs['value'], 'ccm_CertAddr': '********',
              'ccm_LinkMan': soup.find(attrs={"name": "ccm_LinkMan"}).attrs['value'],
              'ccm_LinkPhone': soup.find(attrs={"name": "ccm_LinkPhone"}).attrs['value'], 'ccm_HomeTel': '',
              'ccm_OfficeTel': '', 'ccm_MobileTel': '',
              'ccm_PostCode': soup.find(attrs={"name": "ccm_PostCode"}).attrs['value'], 'ccm_LinkAddr': '********',
              'ccm_Email': '', 'ccm_HomePage': '', 'ccm_IsMergeBill': '1',
              'ccm_CreditLevel': soup.find(attrs={"name": "ccm_CreditLevel"}).attrs['value'],
              'ccm_OwnerAreaID': soup.find(attrs={"name": "ccm_OwnerAreaID"}).attrs['value'],
              'ccm_OrgID': soup.find(attrs={"name": "ccm_OrgID"}).attrs['value'], 'ccm_RegStatus': '1',
              'ccm_Notes': soup.find(attrs={"name": "ccm_Notes"}).attrs['value'], 'ccm_ResponseCustMgr': '',
              'ccm_CurrentCustMgr': '', 'ccm_InLevel': soup.find(attrs={"name": "ccm_InLevel"}).attrs['value'],
              'ccm_TownID': '',
              'ccm_VipTypeStateDate': soup.find(attrs={"name": "ccm_VipTypeStateDate"}).attrs['value'],
              'ccm_NetServGrade': '', 'ccm_CustAddrArray': '[]', 'ccm_CustBillArray': '[]', 'ccm_IsEncrypt': '1',
              'ccm_starLevel': soup.find(attrs={"name": "ccm_starLevel"}).attrs['value'],
              'ccm_IsFaceChk': soup.find(attrs={"name": "ccm_IsFaceChk"}).attrs['value'],
              'ccregister': soup.find(attrs={"name": "ccregister"}).attrs['value'],
              'ccnotRegister': soup.find(attrs={"name": "ccnotRegister"}).attrs['value'], 'csm_ObjectID': '',
              'csm_RandomNum': '', 'csdirect': soup.find(attrs={"name": "csdirect"}).attrs['value'],
              'csm_EntityID': soup.find(attrs={"name": "csm_EntityID"}).attrs['value'],
              'csm_EntityName': cn_soup('csm_EntityName'), 'csm_CreateDate': cn_soup('csm_CreateDate'),
              'csm_Status': cn_soup('csm_Status'), 'csm_StatusDate': '******',
              'csm_EditStatus': cn_soup('csm_EditStatus'), 'csm_Region': '200', 'csm_Password': cn_soup('csm_Password'),
              'csm_ProductID': cn_soup('csm_ProductID'), 'csm_ServNumber': cn_soup('csm_ServNumber'),
              'csm_RegisterOrgID': cn_soup('csm_RegisterOrgID'), 'csm_OwnerOrgID': cn_soup('csm_OwnerOrgID'),
              'csm_AccountOid': cn_soup('csm_AccountOid'), 'csm_CustomerOid': cn_soup('csm_CustomerOid'),
              'csm_AuthType': 'AuthCheckB', 'csm_MobileType': 'mbtpNml', 'csm_AreaID': '', 'csm_PayMode': '1',
              'csm_StopKey': cn_soup('csm_StopKey'), 'csm_Brand': cn_soup('csm_Brand'),
              'csm_StartDate': cn_soup('csm_StartDate'), 'csm_InvalidDate': cn_soup('csm_InvalidDate'),
              'csm_SettleDay': '1', 'csm_Enum': cn_soup('csm_Enum'), 'csm_Imsi': cn_soup('csm_Imsi'), 'csm_Credit': '0',
              'csm_SubsProduct': '[]', 'csm_IsDefaultTelNum': '1', 'csm_BelongRegion': '0', 'csm_TargetRegion': '0',
              'csm_CretLevel': '', 'csgotone': cn_soup('csgotone'), 'csnotGotone': cn_soup('csnotGotone'),
              'cam_ObjectID': '', 'cam_RandomNum': '', 'cadirect': cn_soup('cadirect'),
              'cam_EntityID': cn_soup('cam_EntityID'), 'cam_EntityName': cn_soup('cam_EntityName'),
              'cam_CreateDate': cn_soup('cam_CreateDate'), 'cam_Status': cn_soup('cam_Status'),
              'cam_StatusDate': cn_soup('cam_StatusDate'), 'cam_EditStatus': '0', 'cam_Region': '200',
              'cam_CustID': cn_soup('cam_CustID'), 'cam_GroupAcctID': '', 'cam_PrePayType': 'pptpPost',
              'cam_AccountType': 'actpCmn', 'cam_OverDraft': '0', 'cam_ControlScheme': '0',
              'cam_EntrustTel': cn_soup('cam_EntrustTel'), 'cam_OrgID': cn_soup('cam_OrgID'), 'cam_NotifyType': '0',
              'cam_NotifyValue': '0', 'cam_InvPrintType': 'InvPTbillfee', 'cam_Notes': '', 'cam_PayChannelArray': '[]',
              'cam_CustBillArray': '[]', 'cam_UrgeInfos': '[]', 'cam_SettleAccount': '', 'cam_IsDefault': '1',
              'cam_BillInvoiceMailArray': '[]', 'cam_NotifyValueDisplay': '0',
              'cam_CreateDateDisplay': cn_soup('cam_CreateDateDisplay'), 'com_ObjectID': '', 'com_RandomNum': '',
              'comenuId': cn_soup('comenuId'), 'codirect': 'FALSE', 'com_EntityID': 'AGZGT0000829',
              'com_EntityName': cn_soup('com_EntityName'), 'com_CreateDate': cn_soup('com_CreateDate'),
              'com_Status': cn_soup('com_Status'), 'com_StatusDate': cn_soup('com_StatusDate'), 'com_EditStatus': '0',
              'com_Region': '200', 'coerrorInfoForControl': '', 'conodeID': 'AGZGT0000829',
              'conodeName': cn_soup('conodeName'), 'conodeParentID': cn_soup('conodeParentID'),
              'coentityID': 'AGZGT0000829', 'cootherParam': cn_soup('cootherParam'), 'cochecked': cn_soup('cochecked'),
              'com_MenuID': cn_soup('com_MenuID'), 'com_ServNum': '', 'com_TouchNum': '',
              'com_Password': cn_soup('com_Password'), 'com_OrgID': cn_soup('com_OrgID'), 'com_RoamOrgID': '',
              'com_PassChangeDate': cn_soup('com_PassChangeDate'), 'com_OperType': cn_soup('com_OperType'),
              'com_Manager': '0', 'com_Level': '', 'com_ContactPhone': '13800138000',
              'com_MacAddress': cn_soup('com_MacAddress'), 'com_OnDuty': '0', 'com_ShareStore': '', 'com_BirthDay': '',
              'com_WorkDate': '', 'com_CertID': '', 'com_Sex': '', 'com_EducationLevel': '', 'com_TotalLevel': '',
              'com_SkillLevel': '', 'com_TrainLevel': '', 'com_ComityLevel': '', 'com_Operator_type': '0',
              'com_NativeHome': '', 'com_graduateDate': '', 'com_IsMarray': '0', 'com_PolityFace': '',
              'com_HomeAddress': '', 'com_JobLive': '', 'com_NowPostID': '', 'com_BloodType': '', 'com_Healthy': '',
              'com_Character': '', 'com_Enjoyful': '', 'com_PriSocietyRelation': '', 'com_FamilyDes': '',
              'com_StarLevel': '', 'com_AssessRec': '', 'com_hr_status': '1', 'com_Restrict_time': '0',
              'com_Start_time': '0', 'com_End_time': '24', 'com_Enable_gprs': '0', 'com_Gprs_starttime': '0',
              'com_Gprs_endtime': '0', 'com_Check_mac': '0', 'com_Mac': '', 'com_IPAddress': '10.244.110.143',
              'costartUsingTime': cn_soup('costartUsingTime'), 'coendUsingTime': cn_soup('coendUsingTime'),
              'com_QueueID': '', 'com_InvVersion': '', 'com_areaID': '', 'servNumber': cn_soup('servNumber'),
              'transmit': cn_soup('transmit'), 'recType': '', 'stopKeyValue': cn_soup('stopKeyValue'),
              'remotemac': '08-00-27-44-EC-99'}
    s = r.post(url3, data=param3, cookies=cn_cookies3, headers=header2, auth=_auth, proxies=_proxies)
    return s

def iot_phone_query_base(_r, phone_num, _proxies, _auth, querytype=None):
    s1 = iot_phone_query_base_setp1(_r, phone_num, _proxies, _auth, querytype)

    # 将iot_phone_query_base_setp1查询信息返回
    _result = None
    if type(s1) is tuple:
        _result = s1[1]
        s1 = s1[0]

    iot_phone_query_base_setp2(_r, s1, phone_num, _proxies, _auth)
    return _result

def iot_puk(r,  _proxies, _auth):
    url = 'http://10.253.61.8/nguniteview/layoutAction.do?method=showView&ownerType=1&viewId=314'
    param = {'width': 767, 'height': '14'}
    s = r.post(url, data=param, auth=_auth, proxies=_proxies)
    soup = BeautifulSoup(s.text, 'lxml')
    _result = soup.select('td')[3].text
    return _result


# 判断输入值是否在指定的文件里面，第一次为徕纳500而设置
def process_matching_infile(_input, _file):
    _content = ''

    # _file格式："client/laina500.txt"
    with open(_file, "r") as file:
        for line in file:
            _line = ''.join(line).split()[0]
            if _line == _input:
                _content = _line
                break
    if _content == '':
        return False
    else:
        return True


def cn_cookies2(_cookies, cn_phoneNum):
    cookies = dict()
    for i in _cookies.get_dict('10.253.61.8'):
        cookies[i] = _cookies.get(i, '', '10.253.61.8')
    cookies['bsacKF'] = 'NGCRM_BOSS'
    cookies['com.huawei.boss.CONTACTID'] = 'undefined'
    cookies['com.huawei.boss.CURRENT_MENUID'] = 'ServiceOnStopOrStart'
    cookies['com.huawei.boss.CURRENT_TAB'] = 'BOSS%5E' + cn_phoneNum + '%5EServiceOnStopOrStart%7E' + cn_phoneNum
    cookies['com.huawei.boss.CURRENT_USER'] = cn_phoneNum
    cookies['MACAddr'] = 'null'
    cookies['sDNSName'] = '3B8MB8'
    return cookies


def stop_and_open(_r, _type, phone, _proxies, _auth):
    iot_phone_query_base_setp1(_r, phone, _proxies, _auth)

    url = 'http://10.253.61.8/ngcustcare/common/submits/unitCommonSubmit.action?flow=productOrientedFlow&version=1.01'
    s = _r.get(url, auth=_auth, proxies=_proxies)
    soup = BeautifulSoup(s.text, 'lxml')
    _submits = soup.find(attrs={'name': 'submits/unitCommonSubmit'}).attrs['value']

    url = 'http://10.253.61.8/ngcustcare/custsvc/stopopen/stopOpenCommit.action'
    param = ''
    if _type == '申请开机':
        param = {'stopOpenType': '00030000', 'stopOpenReason': 'd', 'stopOpenMemo': '',
                 'hiddenTokenName': 'submits/unitComamonSubmit', 'submits/unitCommonSubmit': _submits}
    cn_cookies3 = cn_cookies2(_r.cookies, phone)
    s = _r.post(url, data=param, auth=_auth, proxies=_proxies, cookies=cn_cookies3)
    soup = BeautifulSoup(s.text, 'lxml')
    _hiddenTokenName_value = soup.find(attrs={"name": "fee/calculate"}).attrs['value']

    url = 'http://10.253.61.8/ngcustcare/common/fee/pay.action'
    param = {'PreBussOrderId': '', 'withdrawGoods': '', 'payTypeBean.cashAmt': '', 'payTypeBean.chequeAmt': '',
             'payTypeBean.bankId': '', 'payTypeBean.bankName': '', 'payTypeBean.chequeNum': '',
             'payTypeBean.cardAmt': '', 'payTypeBean.posNum': '', 'payTypeBean.confirmPosNum': '',
             'payTypeBean.weiXinPayAmt': '', 'payTypeBean.weiXinPayNum': '', 'payTypeBean.aliPayAmt': '',
             'payTypeBean.orderId': '', 'payTypeBean.aliPayPayNum': '', 'payTypeBean.newSeparatePayAmt': '',
             'payTypeBean.orderId': '', 'payTypeBean.newSeparatePayNum': '', 'payTypeBean.preAuthSeparatePayAmt': '',
             'payTypeBean.orderId': '', 'payTypeBean.preAuthSeparatePayNum': '', 'payTypeBean.acctCash': '',
             'payTypeBean.acctId': '-1', 'payTypeBean.acctPayCash': '', 'payTypeBean.acctPayId': '-1',
             'payTypeBean.scoreCash': '', 'payTypeBean.score': '', 'payTypeBean.scoreTransRule': '1/1',
             'payTypeBean.m': '0', 'payTypeBean.mTransRule': '1/1', 'payTypeBean.bankAmt': '',
             'payTypeBean.posautocardAmt': '', 'payTypeBean.posautocardNum': '', 'payTypeBean.posautoTerminalno': '',
             'payTypeBean.posautoReferno': '', 'payTypeBean.posautoMerchantno': '', 'payTypeBean.posnotautoAmt': '',
             'payTypeBean.posnotautocardNum': '', 'payTypeBean.posnotautoTerminalno': '',
             'payTypeBean.posnotautoReferno': '', 'payTypeBean.posnotautoMerchantno': '', 'payTypeBean.separateAmt': '',
             'payTypeBean.separateBankId': 'GH', 'payTypeBean.separateBankName': '%E5%B7%A5%E8%A1%8C',
             'payTypeBean.separateBankAcct': '', 'payTypeBean.separateBankUserName': '',
             'payTypeBean.separatePosNum': '', 'payTypeBean.limitCash': '', 'payTypeBean.unlimitCash': '',
             'BARGAINFEEXML': '',
             'CHANGEFEEBYBARGAINXML': '@260@263xml@232version@261@2341@2460@234@232encoding@261@234UTF@2458@234@263@262@260huawei@295call@262@260i@262common@247fee@247@242@260@247i@262@260e@262changeFeeByBargain@260@247e@262@260p@262@260m@262@260n@2620@260@247n@262@260t@262a@260@247t@262@260v@262@260@247v@262@260@247m@262@260m@262@260n@2621@260@247n@262@260t@262a@260@247t@262@260v@262@260@247v@262@260@247m@262@260@247p@262@260@247huawei@295call@262&UPDATEPAYTYPEBYPAGEDATAXML=@260@263xml@232version@261@2341@2460@234@232encoding@261@234UTF@2458@234@263@262@260huawei@295call@262@260i@262common@247fee@247@242@260@247i@262@260e@262updatePayTypeByPageData@260@247e@262@260p@262@260m@262@260n@2620@260@247n@262@260t@262a@260@247t@262@260v@262@260@247v@262@260@247m@262@260@247p@262@260@247huawei@295call@262',
             'reccustinfo_name': '', 'reccustinfo_phone': '', 'reccustinfo_certificateType': 'IdCard',
             'reccustinfo_certificateNum': '440103198607251838', 'reccustinfo_address': '', 'emergencyContactNo': '',
             'reccustinfo_note': '', 'invoicePrintMode': '', 'hiddenTokenName': 'fee%2Fcalculate',
             'fee%2Fcalculate': _hiddenTokenName_value, 'receiptNumber': '00000000', 'assembleInvoice': '0',
             'invoiceNumber': '00000000', 'elecInvoiceServNumber': phone, 'isForPaging': 'OLD', 'changeEnumRecType': ''}
    s = _r.post(url, data=param, auth=_auth, proxies=_proxies, cookies=cn_cookies3)
    return ''.join(s.text).split()[0]


















