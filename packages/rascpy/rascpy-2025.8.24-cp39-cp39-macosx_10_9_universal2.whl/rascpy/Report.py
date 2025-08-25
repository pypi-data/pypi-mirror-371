# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from .Tool import trans_y
from .Performance import perf_summary
from .Lan import lan

def write_performance(datas,target_label=None,cut_data_name=None,wide=0.05,thin=0.01,thin_head=10,lift=None,score_reverse=True,writer=None,sheet_name=lan['Performance of the model'],filePath=None):
    '''
    将数据集的性能指标写入excel中。包括：
    1.对模型的输出进行等频划分，观察每个区间段的数量，分布，比例，累计数量，累积分布，累积比例，ODDS，Lift等信息进行汇总
    2.lift，ks，auc

    Parameters
    ----------
    datas : dict{str,tuple(y_true,y_hat,weight)}
        所有需要汇总模型性能的数据集.
        key是数据集的名称，value是一个tuple结构，里面存储的是y_true,y_hat,weight
        
    target_label : dict, optional
        将target中的哪个取值定义为事件发生，哪个取值定义为事件未发生。
        keys的取值只能是unevent或event
        values的取值要根据y取值填写
        默认:{'unevent':0,'event':1}.
        
    cut_data_name : str, optional
        按照哪个数据集对模型的输出进行等频划分. 
        None：按照每个数据集自己的分布进行等频划分
        究竟是选择用同一数据集还是用各自数据集计算等频分割结点取决于使用者的关注点和自身业务。使用同一数据集（通常是train），除了反映模型效能，还能反映模型输出的稳定性和模型在不同数据集上打分的差异。如果使用各自的数据集计算等频分割结点，则能反映模型在每份数据上更真实的效能（通常会比使用同一数据集的效能要高）。
        举一个例子：假设模型用于排序业务（如：将得分排序后按照一定比例通过某项申请），如果使用者对所有业务申请使用同一个阈值，则考虑使用同一数据集计算分割结点。如果使用者对不同业务申请定制不同的阈值，则考虑使用各自的数据集计算分割结点。
        使用相同或不同数据集来计算分割结点需要使用者结合自身的业务应用场景来综合判断。
        默认：None.
        
    wide : float, optional
        对模型的输出进行等频分组，该参数是用户期望的每组占比。依赖于Cutter模块的强大功能，即使打分分布偏斜，也能给出最接近wide的分组。
        默认： 0.05.
        
    thin : float, optional
        与wide含义相同，但是比wide分的更细。有的业务可能不只是需要关注整体情况，还需要关注事件发生率最高（或最低）的那一小部分的识别效率（如召回率，召准率等），则可以通过配置thin来实现。如果thin不为None，则函数会返回两个等频分组的模型指标统计表，一个更宽的wide模型指标统计表，和一个更窄的thin模型指标统计表。
        默认： None.
        
    thin_head : int, optional
        thin越小则等频分组数越多，更窄的thin模型指标统计表就会越长，看起来不是很方便，通常使用thin的目的只是为了关注头部的数据，所以通过thin_head可控制thin模型指标统计表的长度，只保留前thin_head个组
        如果thin为None，则会自动忽略thin_head
        如果thin_head为None，则会将所有thin的分组全部保留
        默认： 10.
        
    lift : tuple(int,...), optional
        计算对应的lift值
        例：(1,5,10,20)，代表计算模型的lift1,lift5,lift10,lift20
        None：不计算模型的lift
        默认： None.
        
    score_reverse : boolean, optional
        告知打分分值与事件发生率的关系，以便该函数给出人性化的展示
        True：事件发生概率越高，得分越低
        False: 事件发生概率越高，得分越高
        默认:True
        
    writer : writer, optional
        一个excel写入的writer，如果将当前信息与其他信息合并输出到同一个excel中，则使用writer比较方便，否则使用filePath比较方便
        
    sheet_name : str, optional
        将模型的性能指标写入到该sheet页中
        
        
    filePath : str, optional
        优先使用writer，如果writer为None，则使用filePath指定的excel文件位置
        writer和filePath不能同时为None
        
    
    Returns
    -------
    wide_perfs : dict<str,pd.DataFrame>
        返回每个数据集按照wide对模型输出进行等频分组后的每个区间段的数量，分布，比例，累计数量，累积分布，累积比例，ODDS，Lift等信息进行汇总
        
    thin_perfs : dict<str,pd.DataFrame>
        返回每个数据集按照thin对模型输出进行等频分组后的每个区间段的数量，分布，比例，累计数量，累积分布，累积比例，ODDS，Lift等信息进行汇总
        
    lifts : dict<str,list>
        返回各个数据集用户指定的lift
        如果用户指定的lift为None，则该值也返回None
        
    ks : dict<str,float>
        返回各个数据集的ks
        
    auc : dict<str,float>
        返回各个数据集的auc

    '''
    
    wide_perfs,thin_perfs,lifts,ks,auc = perf_summary(datas,target_label,cut_data_name,wide,thin,thin_head,lift,score_reverse)
    gap = 7
    row_curr = gap
    ts = []
    manu_close = False
    if writer is None and filePath is not None:
        writer = pd.ExcelWriter(filePath) 
        manu_close=True
    for k in datas:
        for perf in [wide_perfs,thin_perfs]:
            if perf is None:
                continue
            tmp = perf[k].copy()
            tmp.reset_index(inplace=True)
            tmp[lan['Sample']]=k
            tmp.set_index([lan['Sample'],lan['Label']],inplace=True)
            tmp.columns = pd.MultiIndex.from_tuples([
                (lan['Quantity'],lan['Total amount']),(lan['Quantity'],lan['Event']),(lan['Quantity'],lan['Unevent'])
                ,(lan['Cumulative quantity'],lan['Total amount']),(lan['Cumulative quantity'],lan['Event']),(lan['Cumulative quantity'],lan['Unevent'])
                ,(lan['Distribution'],lan['Total amount'] ),(lan['Distribution'],lan['Event']),(lan['Distribution'],lan['Unevent'])
                ,(lan['Cumulative distribution'],lan['Total amount']),(lan['Cumulative distribution'],lan['Event']),(lan['Cumulative distribution'],lan['Unevent'])
                ,(lan['Event rate'],lan['Interval']),(lan['Event rate'],lan['Cumulative'])
                ,('ODDS',lan['Interval']),('ODDS',lan['Cumulative'])
                ,(' ',lan['Lift'])
                ])
            tmp.to_excel(writer, sheet_name=sheet_name,startcol=4,startrow=row_curr)
            row_curr+=tmp.shape[0]
            row_curr+=gap
    
        t = pd.Series({lan['Sample']:k,'KS':ks[k],'AUC':auc[k]})
        if lift is not None:
            for i,l in enumerate(lift):
                t['%s %d'%(lan['Lift'],l)] = lifts[k][i]
        ts.append(t)
    pd.DataFrame(ts).set_index(lan['Sample']).to_excel(writer, sheet_name=sheet_name , startcol=30,startrow=10)
    if manu_close:
        writer.close()
    return  wide_perfs,thin_perfs,lifts,ks,auc  

# '样本Y统计'
def write_y_stat(datas,y_stat_group_cols = None,weight_col=None,y_col='y',y_label=None,writer=None,sheet_name=lan['0113'],filePath=None):  
    '''
    对所有数据集的Y值分布进行统计，如果指定y_stat_group_cols，则按照y_stat_group_cols分组后再进行统计

    Parameters
    ----------
    datas : dict{str,dict{str,dataframe}}
        datas是个二级嵌套dict结构，第一个str是该数据集的用途，第二个str是该数据集的名称。
        例：{'model_data':{'train':df_train,'test':df_test},'perf_data':{'client1':df1,'client2':df2},'oot_data':{'time1':df_time1,'time2':df_time2}}
        
    y_stat_group_cols : list, optional
        用户指定的用于分组统计Y的一个或多个变量 
        None：不指定分组
        默认：None.
        
    weight_col : str, optional
        样本权重列名. 
        None:所有样本权重一样
        默认：None.
        
    y_col : str, optional
        样本y值的列名
        默认：'y'.
        
    y_label : dict, optional
        将数据中的y_col列的哪个取值定义为事件发生，哪个取值定义为事件未发生。
        keys的取值只能是unevent或event
        values的取值要根据y的取值填写
        默认:{'unevent':0,'event':1}.
        
    writer : writer, optional
        一个excel写入的writer，如果将当前信息与其他信息合并输出到同一个excel中，则使用writer比较方便，否则使用filePath比较方便
        
    sheet_name : str, optional
        将y统计结果写入到该sheet页中
        
        
    filePath : str, optional
        优先使用writer，如果writer为None，则使用filePath指定的excel文件位置
        writer和filePath不能同时为None

    Returns
    -------
    None.

    '''
    dfs = []   
    import copy
    if y_stat_group_cols is not None:
        tmp_group_cols = copy.copy(y_stat_group_cols)
    else:
        tmp_group_cols = []
    
    if y_col not in tmp_group_cols:
        tmp_group_cols.append(y_col)
    if weight_col is not None and weight_col not in tmp_group_cols:
        tmp_group_cols.append(weight_col)

    def _f1(tmp,y_label):
        if y_label is not None:
            y_value = tmp[y_col].apply(trans_y, y_label=y_label)
        else:
            y_label = tmp[y_col]
        if weight_col is None:
            return np.round(y_value.mean(),4)
        else:
            return np.round((y_value * tmp[weight_col]).sum() / tmp[weight_col].sum(),4)
        
    for k1,v1 in datas.items():
        for k2,v2 in v1.items():
            if y_col not in v2.columns:
                continue     
            tmp_b = True
            for i in tmp_group_cols:
                if i not in v2:
                    tmp_b = False
                    continue
            if not tmp_b:
                continue
            df_count = v2.groupby(tmp_group_cols)[[y_col]].count()
            df_count.columns=[lan['Sample Size']]
            df_count.reset_index(inplace=True)
            if weight_col is not None:
                df_count.rename({'__weight':weight_col},axis=1,inplace=True)
                df_count[lan['Sample Size (Weight)'] ] = (df_count[lan['Sample Size']]*df_count[weight_col]).apply(lambda x:int(np.around(x)))  
            df_count.set_index(tmp_group_cols,inplace=True)
            if weight_col is not None:
                df_count.columns = pd.MultiIndex.from_tuples([('%s[%s]'%(k2,k1),lan['Sample Size']),('%s[%s]'%(k2,k1),lan['Sample Size (Weight)'])])
            else:
                df_count.columns = pd.MultiIndex.from_tuples([('%s[%s]'%(k2,k1),lan['Sample Size'])])  
             
            df_rate_name = lan['Event rate']
            if weight_col is not None:
                df_rate_name+=lan['(Weight)']
            
            if y_stat_group_cols is not None and len(y_stat_group_cols)>0:
                df_rate = v2.groupby(y_stat_group_cols).apply(_f1,y_label=y_label)
            else:
                df_rate = pd.Series([_f1(v2,y_label)])
            
            df_rate.name = df_rate_name
            dfs.append((df_count,df_rate))

    step = 10
    row_curr = step
    manu_close = False
    
    if writer is None and filePath is not None:
        writer = pd.ExcelWriter(filePath) 
        manu_close=True
    
    for m,n in dfs:
        m.to_excel(writer, sheet_name=sheet_name,startcol=4,startrow=row_curr)
        if y_stat_group_cols is None or len(y_stat_group_cols)==0:
            r_add=1
            index=False
        else:
            r_add = 2
            index=True
        n.to_excel(writer, sheet_name=sheet_name,startcol=m.shape[1]+len(tmp_group_cols)+4,startrow=row_curr+r_add,index=index)
        row_curr = row_curr+m.shape[0]+step 
        
    if manu_close:
        writer.close()
   
def write_feature_select(indices,filtered_cols,used_cols,filters_middle_data,var_describe_file_path=None,writer=None,sheet_name=lan['Selection of variables'],filePath=None):
    '''
    将变量选择的结果写入到excel中
    
    Parameters
    ----------
    indices : dict{str,Series}
        把各个变量的指标值在报告中展示出来
        key为指标名称
        vaue为每个变量在key指标上的取值
        
    filtered_cols : dict{str,str}
        每个变量被过滤掉的原因，多个原因用回车分割。
        原因包括，不满足指标的阈值（有几个指标不满足就列出几个），和逻辑回归删除
        
    used_cols : dict<str,str>
        每个变量入模的原因，包括：
        逻辑回归引入，用户强制引入等
    
    filters_middle_data : dict{str,dataframe}
        将用户传入的变量指标的中间过程数据输出到excel中
        str会作为sheet的名称
        
    var_describe_file_path : str, optional
        变量描述文件
        该文件的第一列记录变量的名称，名称必须与模型数据的变量一致，大小写也要相同
        文件除第一列外其他的列会被显示在变量选择对应的excel sheet页中，方便用户查看
        
    writer : writer, optional
        一个excel写入的writer，如果将当前信息与其他信息合并输出到同一个excel中，则使用writer比较方便，否则使用filePath比较方便
        
    sheet_name : str, optional
        将结果写入到该sheet页中
        
        
    filePath : str, optional
        优先使用writer，如果writer为None，则使用filePath指定的excel文件位置
        writer和filePath不能同时为None

    Returns
    -------
    None.

    '''
    used_cols = pd.Series(used_cols,name=lan['Variable in model'])
    filtered_cols = pd.Series(filtered_cols,name=lan['0109'])
    if len(indices)!=0:
        indices = pd.concat(indices,axis=1)
        tmp = pd.concat([indices,used_cols,filtered_cols],axis=1)
    else:
        tmp = pd.concat([used_cols,filtered_cols],axis=1)
    tmp,_ = merge_desc(tmp,var_describe_file_path)
    
    manu_close = False
    if writer is None and filePath is not None:
        writer = pd.ExcelWriter(filePath) 
        manu_close=True
        
    tmp.to_excel(writer, sheet_name=sheet_name)   
    
    for k,v in filters_middle_data.items():
        v.to_excel(writer, sheet_name=k)
        
    if manu_close:
        writer.close()
        
def write_reg_clf(clf_perf,clf_coef,del_reason,step_proc,var_describe_file_path,writer=None,sheet_name=lan['Model Info'],filePath=None):
    '''
    将Reg_Step_Wise_MP.LogisticReg.fit()的返回结果输出到excel中

    Parameters
    ----------
    clf_perf : 
        Reg_Step_Wise_MP.LogisticReg.fit()的返回值clf_perf
        
    clf_coef : 
        Reg_Step_Wise_MP.LogisticReg.fit()的返回值clf_coef
        
    del_reason : 
        Reg_Step_Wise_MP.LogisticReg.fit()的返回值del_reason
        
    step_proc : 
        Reg_Step_Wise_MP.LogisticReg.fit()的返回值step_proc
        
    var_describe_file_path : str, optional
        变量描述文件
        该文件的第一列记录变量的名称，名称必须与模型数据的变量一致，大小写也要相同
        文件除第一列外其他的列会被显示在模型选择对应的excel sheet页中，方便用户查看
        
    writer : writer, optional
        一个excel写入的writer，如果将当前信息与其他信息合并输出到同一个excel中，则使用writer比较方便，否则使用filePath比较方便
        
    sheet_name : str, optional
        将结果写入到该sheet页中
        
    filePath : str, optional
        优先使用writer，如果writer为None，则使用filePath指定的excel文件位置
        writer和filePath不能同时为None
    Returns
    -------
    None.

    '''
    manu_close = False
    if writer is None and filePath is not None:
        writer = pd.ExcelWriter(filePath) 
        manu_close=True
        
    row_num=2
    clf_perf.to_excel(writer, sheet_name=sheet_name,header=False,index=False,startrow=row_num)
    row_num = row_num+clf_perf.shape[0]+4
    clf_coef,_ = merge_desc(clf_coef,var_describe_file_path)
    clf_coef.index.name=lan['Vars']
    clf_coef.to_excel(writer, sheet_name=sheet_name,startrow=row_num)
    row_num = row_num+clf_coef.shape[0]+4
    step_proc.to_excel(writer, sheet_name=sheet_name,startrow = row_num) 
    row_num = row_num+step_proc.shape[0]+4
    del_reason.index.name=lan['Vars']
    del_reason.to_excel(writer, sheet_name=sheet_name,startrow = row_num)
    if manu_close:
        writer.close()
    
def write_card(Dcard,base_points,base_event_rate,pdo,train_bins_stat,stand_coef,var_describe_file_path,writer,sheet_name=lan['Score card'],filePath=None):
    '''
    将评分卡输入到excel中,包括：
    各个变量每个分箱的得分，评分卡分数校准的参数，变量权重

    Parameters
    ----------
    Dcard : 
        ScoreCard.CardFlow.card
        
    base_points : float
        基准分
        
    base_event_rate : float
        基准分对应的基准事件率
        
    pdo : float
        pdo
        
    stand_coef : TYPE
        Reg_Step_Wise_MP.LogisticReg.fit()的返回值clf_coef['Standardized Estimate']
        
    writer : writer, optional
        一个excel写入的writer，如果将当前信息与其他信息合并输出到同一个excel中，则使用writer比较方便，否则使用filePath比较方便
              
    sheet_name : str, optional
        将y统计结果写入到该sheet页中
              
    filePath : str, optional
        优先使用writer，如果writer为None，则使用filePath指定的excel文件位置
        writer和filePath不能同时为None

    Returns
    -------
    None.

    '''
    df_card = pd.concat(Dcard)
    df_card.reset_index(inplace=True)
    del df_card['level_1']
    df_card.rename({'level_0':lan['Vars']},axis=1,inplace=True)
    index_cols = [lan['Vars']]
    df_card,desc = merge_desc(df_card,var_describe_file_path,col=lan['Vars'])
    if desc is not None:
        index_cols.extend(desc.columns)
    df_card[lan['Bins']] = df_card[lan['Bins']].apply(str)
    index_cols.append(lan['Bins'])
    df_card.set_index(index_cols,inplace=True)
    df_card.to_excel(writer,sheet_name=sheet_name)
    
    pd.Series({lan['Base points']:base_points,lan['Base ODDS']:np.around((1-base_event_rate)/base_event_rate,1),lan['Base event rate']:base_event_rate,'PDO':pdo},name=lan['Scoring calibration']).to_excel(writer,startcol=df_card.shape[1]+len(index_cols)+4,sheet_name=sheet_name)
    
    diffs = pd.Series()
    for k,v in Dcard.items():
        diffs[k] = Dcard[k][lan['Points']].max() - Dcard[k][lan['Points']].min()
    sc = stand_coef.loc[stand_coef.index!='const']
    sc = np.abs(sc)
    # IVs = IVs/IVs.sum()
    diffs = diffs
    diffs = diffs/diffs.sum()
    sc = sc/sc.sum()
    tmp = pd.concat([sc,diffs],axis=1)#,IVs
    tmp.columns = pd.MultiIndex.from_tuples([(lan['Variable weight'],lan['Standardized coefficients']),(lan['Variable weight'],lan['Max difference'])])
    tmp.index.name=lan['Vars']
    tmp = tmp.apply(np.around,decimals=2)
    tmp.to_excel(writer,startcol=df_card.shape[1]+len(index_cols)+8,sheet_name=sheet_name)
    
def merge_desc(df,var_describe_file_path=None,col=None,index=True):
    desc = None
    if var_describe_file_path is not None:
        desc = pd.read_excel(var_describe_file_path,index_col=0)
        if col is not None:
            df = df.merge(desc,left_on=col,right_index=True,how='left')
        elif index:
            df = df.merge(desc,left_index=True,right_index=True,how='left')      
    return df,desc

def bfy_df_like_excel(df_grid,writer,sheet_name='Sheet1',default_decimal=None,text_lum=0.5,red_max=True,row_num=0,col_num=0,row_gap=2,col_gap=2):
    '''
    将所有表格输出到一张excel的sheet中
    例：
    df_grid=[]
    df_rows1=[]#输出到第1行的表格放入此list中
    df_rows2=[]#输出到第2行的表格放入此list中
    df_rows3=[]#输出到第3行的表格放入此list中
    df_rows4=[]#输出到第4行的表格放入此list中
    #注：此处的行不是excel中“行”的概念
    df_grid.append(df_rows1)
    df_grid.append(df_rows2)
    df_grid.append(df_rows3)
    df_grid.append(df_rows4)
    
    df1 = pd.DataFrame(np.random.randn(10, 4), columns=['A1', 'B1', 'C1', 'D1'])
    df1['SCORE_BIN']=['[0,100)','[100,200)','[200,300)','[300,400)','[400,500)','[500,600)','[600,700)','[700,800)','[800,900)','[900,1000]']
    #将df1输出到第1行的第1个表格中
    df_rows1.append({'df':df1,'title':['DF1','notAnum'],'percent_cols':df1.columns,'color_gradient_sep':True})
    
    df2 = pd.DataFrame(np.random.randn(1, 4), columns=['A2', 'B2', 'C2', 'D2'])
    #将df2输出到第1行的第2个表格中
    df_rows1.append({'df':df2,'color_gradient_cols':['A2','D2'],'title':['percent_BC','gradient_AD'],'percent_cols':['B2','C2']})
    
    df3 = pd.DataFrame(np.random.randn(15, 4), columns=['A3', 'B3', 'C3', 'D3'])
    #将df3输出到第2行的第1个表格中
    df_rows2.append({'df':df3,'color_gradient_cols':['B3'],'title':['long table']})
    
    df4 = pd.DataFrame(np.random.randn(4, 4), columns=['A4', 'B4', 'C4', 'D4'])
    #将df4输出到第2行的第2个表格中
    df_rows2.append({'df':df4,'color_gradient_sep':False})
    
    df5 = pd.DataFrame(np.random.randn(10, 5), columns=['A5', 'B5', 'C5', 'D5', 'E5'])
    #将df5输出到第3行的第1个表格中
    df_rows3.append({'df':df5,'color_gradient_sep':True,'not_color_gradient_cols':['C5']})
    
    df6 = pd.DataFrame({'A6':[1,2,3,4],'B6':[0.1,1.2,100.5,7.4]})
    #将df6输出到第4行的第1个表格中
    df_rows4.append({'df':df6,'color_gradient_sep':True,'percent_cols':['A6']})
    
    #两种输出方式，根据实际需要任选其一即可
    r,c = bfy_df_like_excel(df_grid,'Demo.xlsx',sheet_name='demo',red_max=False,row_num=4,col_num=4,row_gap=2,col_gap=2)
    or
    with pd.ExcelWriter('Demo.xlsx') as writer:
        r,c = bfy_df_like_excel(df_grid,writer,sheet_name='demo',red_max=False,row_num=4,col_num=4,row_gap=2,col_gap=2)
    print(r,c)

    Parameters
    ----------
    df_grid : 一个2维的list
        [
            [dict,dict,...],#第1行
            [dict,dict,...],#第2行
            ...
        ]  
        每个dict代表一个DataFrame（table）的设置
        dict的key含义：
            df:待输出的DataFrame
            title:参看bfy_df_like_excel_one.df
            percent_cols:参看bfy_df_like_excel_one.percent_cols
            color_gradient_cols:参看bfy_df_like_excel_one.color_gradient_cols
            not_color_gradient_cols:参看bfy_df_like_excel_one.not_color_gradient_cols
            color_gradient_sep:参看bfy_df_like_excel_one.color_gradient_sep
            decimal:参看bfy_df_like_excel_one.decimal.如果该df没有设置decimal，则默认使用default_decimal     
            
    writer : str or pandas.ExcelWriter
        指定excel路径，或者是一个已经构建好的ExcelWriter.
        
    sheet_name : str, optional
        指定的excel的sheet.
        默认 'Sheet1'
        
    default_decimal : int , optional
        默认保留的小数位数.如果某个df没有设置decimal，则默认使用default_decimal
        默认 None
        
    text_lum : float, optional
        [0,1]之间的一个数，用来控制文字与色阶的色差大小。text_lum越大越会加大色差。
        当text_lum=0，文本总是黑色
        默认 0.5
        
    red_max : boolean, optional
        True:数值越大颜色越红，数值越小颜色越绿
        False:数值越大颜色越绿，数值越小颜色越红
        默认 True.
        
    row_num : int, optional
        表的起始行编号
        默认 0.
        
    col_num : int, optional
        表的起始列编号
        默认 0.
        
    row_gap : int, optional
        行与行之间的间隔. 
        默认 2.
        
    col_gap : int, optional
        列与列之间的间隔. 
        默认 2.

    Returns
    -------
    int
        所有表格输出完毕后的最后一行.
    int
        所有表格输出完毕后的最后一列.（不是最后一行的最大列）
        例如共有两行，第一行的最大列是5，第二行的最大列是4，则返回5

    '''    
    def _f():
        cur_row_num = row_num
        cur_col_num = col_num
        max_row_num = row_num
        max_col_num = col_num
        for r in df_grid:
            for c in r:
                df = c['df']
                title = c.get('title',[])
                percent_cols = c.get('percent_cols',[])
                color_gradient_cols = c.get('color_gradient_cols',None)
                not_color_gradient_cols = c.get('not_color_gradient_cols',[])
                color_gradient_sep = c.get('color_gradient_sep',None)
                decimal = c.get('decimal',default_decimal)
                
                tmp_row_num,tmp_col_num = bfy_df_like_excel_one(df = df,writer = writer,sheet_name=sheet_name,title=title,decimal=decimal,percent_cols=percent_cols,color_gradient_cols=color_gradient_cols,not_color_gradient_cols=not_color_gradient_cols,color_gradient_sep=color_gradient_sep,text_lum=text_lum,red_max=red_max,row_num=cur_row_num,col_num=cur_col_num)
                
                max_row_num = max(max_row_num,tmp_row_num)
                max_col_num = max(max_col_num,tmp_col_num)
                cur_col_num = tmp_col_num + col_gap
            
            cur_row_num = max_row_num + row_gap
            cur_col_num = col_num
        return max_row_num,max_col_num

    if type(writer) == str:
        with pd.ExcelWriter(writer) as writer:
            r,c = _f()
    else:
        r,c = _f()    
    return r,c
    
def bfy_df_like_excel_one(df,writer,sheet_name='Sheet1',title=[],decimal=None,percent_cols=[],color_gradient_cols=None,not_color_gradient_cols=[],color_gradient_sep=True,text_lum=0.5,red_max=True,row_num=0,col_num=0):
    '''
    将一个dataframe美化成一个excel透视表风格的图表，并输出到指定excel。
    可以做excel的色阶填充和百分比显示（不是格式化成百分比，而是显示成百分比，实际数值和数值类型保持不变）。
    例：
    df1 = pd.DataFrame(np.random.randn(10, 4), columns=['A1', 'B1', 'C1', 'D1'])
    df1['SCORE_BIN']=['[0,100)','[100,200)','[200,300)','[300,400)','[400,500)','[500,600)','[600,700)','[700,800)','[800,900)','[900,1000]']
    r,c = bfy_df_like_excel_one(df1,'df1.xlsx',title=['DF1','any'],percent_cols=df1.columns,color_gradient_sep=True,text_lum=0,row_num=2,col_num=2)#
    print(r,c)

    Parameters
    ----------
    df : DataFrame
        需要美化的dataframe
        
    writer : str or pandas.ExcelWriter
        指定excel路径，或者是一个已经构建好的ExcelWriter.
        
        
    sheet_name : str, optional
        指定的excel的sheet.
        默认 'Sheet1'
        
    title : list, optional
        会将title中的每个文本输出到表格的上方，每个元素占据一个cell 
        The default is [].
        
    decimal : int , optional
        保留的小数位数.自动的排除df中的int型数列和非数字列
        在excel中存储的原始数据不会改变，只是改变了excel的显示，功能与excel中的"设置单元格格式-保留小数"相同
        None:不调整小数位数
        默认 None
        
    percent_cols : list , optional
        需要显示成百分比的列,自动保留百分数的2位小数
        例如：0.23456 -> 23.46%
        在excel中存储的原始数据不会改变，只是改变了excel的显示，功能与excel中的"设置单元格格式-百分比"相同
        会自动的排除其中的int型数列和非数字列
        默认 []
           
    color_gradient_cols : list, optional
        需要展示色阶的列
        None：df中的全部数字列都需要展示色阶
        会自动的排除其中的非数字列
        默认 None.
        
    not_color_gradient_cols : list, optional
        不需要展示色阶的列。not_color_gradient_cols的优先级高于color_gradient_cols
        非数字列会被自动排除，因此不需要在此标记
        默认 [].
        
    color_gradient_sep : boolean, optional
        True:每个单元格的颜色按照其所在列的最大值和最小值来确定
        False:每个单元格的颜色会按照所有参与色阶列全部取值的最大值和最小值来确定。
        默认 True
        
    text_lum : float, optional
        [0,1]之间的一个数，用来控制文字与色阶的色差大小。text_lum越大越会加大色差。
        当text_lum=0，文本总是黑色
        默认 0.5
        
    red_max : boolean, optional
        True:数值越大颜色越红，数值越小颜色越绿
        False:数值越大颜色越绿，数值越小颜色越红
        默认 True.
        
    row_num : int, optional
        表的起始行编号
        默认 0.
        
    col_num : int, optional
        表的起始列编号
       默认 0.

    Returns
    -------
    int
        结尾的row_num（表格右下角的行编号）
    int
        结尾的col_num（表格右下角的列编号）

    '''
    import matplotlib.colors as mcolors
    # percent_cols=[],color_gradient_cols=None,not_color_gradient_cols=[]
    num_cols = set(df.select_dtypes(include=[np.number]).columns)
    float_num_cols  = set(df.select_dtypes(include=[float]).columns) 
    
    percent_cols = list(set(percent_cols) & float_num_cols)
    
    if color_gradient_cols is None:
        color_gradient_cols = list(num_cols)
    else:
        color_gradient_cols = list(set(color_gradient_cols) & num_cols)
        
    if not_color_gradient_cols is not None and len(not_color_gradient_cols)>0:
        color_gradient_cols = list(set(color_gradient_cols) - set(not_color_gradient_cols))
        
    if not color_gradient_sep:
        color_gradient_sep = None
    else:
        color_gradient_sep = 0
        
    def get_map(style):
        if 'map' in dir(pd.io.formats.style.Styler):
            return style.map
        else:
            return style.applymap
        
    def get_map_index(style):
        if 'map_index' in dir(pd.io.formats.style.Styler):
            return style.map_index
        else:
            return style.applymap_index
    
    def _f():
        row_off = 0
        col_off = 0
        if title is not None and len(title) > 0:
            row_off += 1
            col_off += len(title)
            df_title = pd.DataFrame(columns=title)
            title_css = 'color:black;background-color:#dce6f0;text-align:center;font-weight:bold'
            get_map_index(df_title.style)(lambda x:title_css,axis=1).to_excel(writer,startrow=row_num,startcol=col_num,index=False,sheet_name=sheet_name)
        if  red_max:  
            colors = ["#63be7b", "#ffeb84", "#f8696b"]
            # colors = ["#63be7b","#b1d47f",  "#ffeb84","#fcaa78", "#f8696b"]
        else:
            colors = ["#f8696b" ,"#ffeb84","#63be7b"]
            # colors = ["#f8696b" ,"#fcaa78","#ffeb84","#b1d47f", "#63be7b"]
        
        cmap = mcolors.LinearSegmentedColormap.from_list("excel_color_gradient",colors , N=10000)  
        head_css = 'color:black;background-color:#dce6f0;text-align:center;font-weight:bold'
        
        s = get_map_index(df.style)(lambda x:head_css,axis=1)
        
        if decimal is not None:
            s = get_map(s)(lambda v: "number-format: 0.%s;"%('0'*decimal),subset=list(float_num_cols))
            
        if len(percent_cols)>0:
            s = get_map(s)(lambda v: "number-format: 0.00%;",subset=percent_cols)
        
        s = s.background_gradient(cmap=cmap,axis=color_gradient_sep
                                         ,text_color_threshold=text_lum,subset=color_gradient_cols)
        
        s.to_excel(writer,startrow=row_num+row_off,startcol=col_num,sheet_name=sheet_name,index=False)
        row_off += df.shape[0]+1
        col_off = max(df.shape[1],col_off)
        return row_num+row_off,col_num+col_off

    if type(writer) == str:
        with pd.ExcelWriter(writer) as writer:
            r,c = _f()
    else:
        r,c = _f()
        
    return r,c