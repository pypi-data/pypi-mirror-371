# -*- coding: utf-8 -*-
"""
Created on Wed May 28 09:11:15 2025

@author: wangwenhao
"""
from .Tree import auto_xgb
import pandas as pd
from .RejInfer import syn_reject_dat,diff
import numpy as np
from .Lan import lan

def auto_rej_xgb(train_X,train_y,val_X,val_y,rej_train_X,rej_val_X,train_w=None,val_w=None,rej_train_w=None,rej_val_w=None,metric='ks',iter_cost_time=60*5):
    perf_cands,params_cands,clf_cands,vars_cands = auto_xgb(train_X,train_y,val_X,val_y,train_w,val_w,metric=metric,cost_time=60*5,cands_num=1)
    not_rej_clf = clf_cands[0]
    if train_w is None:
        train_w = pd.Series(1,index = train_y.index)
        
    if rej_train_w is None:
        rej_train_w = pd.Series(1,index = rej_train_X.index)
    
    d = np.inf
    last_clf = not_rej_clf
    rej_clf = not_rej_clf#最终的clf
    ite = 0
    X_for_diff = pd.concat([val_X,rej_val_X])
    while(True):
        ite+=1
        syn_train_X,syn_train_y,syn_train_w,_ = syn_reject_dat(last_clf,train_X,train_y,rej_train_X,None,train_w,None,rej_train_w,None)
        
        syn_val_X , syn_val_y , syn_val_w , _ = syn_reject_dat(last_clf,val_X,val_y,rej_val_X,None,val_w,None,rej_val_w,None)
        
        _,_,tmp_clf_cands,_ = auto_xgb(syn_train_X,syn_train_y,syn_val_X,syn_val_y,syn_train_w,syn_val_w,metric=metric,cost_time=iter_cost_time,cands_num=1)
        
        clf = tmp_clf_cands[0]
        tmp_d = np.around(diff(rej_clf,clf,X_for_diff),4)
        print(lan['0172']%ite)
        if tmp_d < d:
            d = tmp_d
            rej_clf = clf
            c=1
            syn_train = (syn_train_X,syn_train_y,syn_train_w)
            syn_val = (syn_val_X , syn_val_y , syn_val_w)
        else:
            c+=1
            if c>2:
                break
        last_clf = clf
    return not_rej_clf,rej_clf,syn_train,syn_val