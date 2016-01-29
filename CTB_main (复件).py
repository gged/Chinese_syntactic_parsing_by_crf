# -*- coding: cp936 -*-
'''
target:pieces parse
piece_parse_sen(sen,flag)
#0 for δ�з�
#1 for ���з�
#2 for ���з֣����д���
author:hdz
time:2014-11-3 20:24:03
'''
import sys
import time
# from get_new_tag import tag_model_class
from get_new_tag2 import tag_model_class
from split_model_test import split_sen
from piece_parse import piece_parsed_main_sen
from piece_joint_parse import get_piece_joint
from CCG_tree import read_tree
from treeWriter import treeWriter
from MultiTree import MultiTree
from read_pos_json import read_pos_json
#from get_pcfg_prob import count_pcfg_prob
import cPickle
#version='_tag_struct_sx3tag_no_xing_real'
#version='_tag_struct_sx3tag_no_xing_real_len_5_BME'
from configure import beam_size
#version='_tag_struct_sx3tag_no_xing_real_len_5_BME_beam_'+str(beam_size)#
#version='_tag_struct_sx3tag_no_xing_real_beam_'+str(beam_size)
version='_tag_struct_sx3tag_no_xing_real_beam_'+str(beam_size)

test_file='files/ctb_8_test_binary2.txt'
result_file='files/ctb_8_test_binary2_res.txt'+version
pcfg_pickle_file='model/CTB_binary_no_xing_pcfg'

def write_file(fn,res):
    with open(fn,'w') as ff:
        ff.write('\n'.join(res).encode('utf8','ignore'))
    #print 'write done'
def CTB_parse_main(sen,tag_models,pcfg_model):    #tag_model_class, sentence
    ##split to pieces##
    pieces=split_sen(sen)
    ##piece parse##
    kbest=piece_parsed_main_sen(pieces,tag_models[0],pcfg_model)
    #return tl
    ##piece joint##
    tree=get_piece_joint(kbest,tag_models[1],pcfg_model)
    #return tl
    #return (pieces,tl,tree)
    return tree
def CTB_parse_sen(sen,flag,tag_models,pcfg_model):
    '''
    sen:a sentence when flag==0,ABC\
        a segmented sentence when flag==1,A B C\
        a word with pos list when flag==2,[word+\t+pos,...]
    flag:a flag for sen data type
    '''
##    if flag==0: #0for δ�з�
##        try:#
##            sen=cut(sen)#get a word list string#unicode
##            #�� �� ���� ��
##            return piece_parse_sen(sen,1)
##        except:
##            print "It's not a sentence."
##    elif flag==1: #1 for ���з�
##        try:
##            try:
##                sen=sen.decode('gbk')
##            except:
##                pass
##            sen=sen.split(' ')#a word list#unicode
##            sen=get_pos(sen)
##            return piece_parse_sen(sen,2)
##        except:
##            print "It's not a segmented sentence."
    if flag==2: #2 for ��pos
        tree=CTB_parse_main(sen,tag_models,pcfg_model)
        return tree
##        try:
##            tree=piece_parse_main(sen)
##            return tree
##        except:
##            print 'error!'
##            return None
    else:
        print 'flag(0~2)'
    return None
def CTB_main(psj=None,sen=None):
##    sen=raw_input('���������ľ���~\n')
##    sen=sen.decode('gbk')
##    print 'sen:',sen
    ###tag model###todo old tag model
    #tag_model=tag_model_class(joint=False)
    #tag_joint_model=tag_model_class(joint=True)
    #tag_models=[tag_model,tag_joint_model]
    tag_models=[{},{}]# empty, tag's model based on crf model
    pcfg_model=cPickle.load(file(pcfg_pickle_file,'r'))
    #tag_models=[tag_model,tag_model]
    wll=[]
    if sen!=None:
        #sen='( (IP (IP (NP-PN (NR �Ϻ�)(NR �ֶ�))(VP (VP (LCP (NP (NT ����))(LC ��))(VP (VCD (VV �䲼)(VV ʵ��))(VP* (AS ��)(NP (CP (IP (VP (VV �漰)(NP (NP (NP (NN ����)(NP* (PU ��)(NP* (NN ó��)(NP* (PU ��)(NP* (NN ����)(NP* (PU ��)(NP* (NN �滮)(NP* (PU ��)(NP* (NN �Ƽ�)(NP* (PU ��)(NN �Ľ�)))))))))))(ETC ��))(NP (NN ����)))))(DEC ��))(NP* (QP (CD ��ʮһ)(CLP (M ��)))(NP (NN ������)(NN �ļ�)))))))(VP* (PU ��)(VP (VP* (VV ȷ��)(AS ��))(NP (DNP (NP (NP-PN (NR �ֶ�))(NP (NN ����)))(DEG ��))(NP* (ADJP (JJ ����))(NP (NN ����))))))))(PU ��)) )'
        #sen=sen.decode('gbk')
        t=read_tree(sen)
        wl=t.get_words()#[(word,pos),,,]
        wll=[wl]
    if psj!=None:
        wll=read_pos_json(psj)
    #0for δ�з�,1 for ���з�,2 for ��pos
    treel=[]
    for wl in wll:
        treel.append(CTB_parse_sen(wl,2,tag_models,pcfg_model))
    #print tree.show()
    return treel
def test_main(tf,resf):#��������,�Ѿ��䷨��������
    # tag_model=tag_model_class(joint=False)
    # tag_joint_model=tag_model_class(joint=True)
    # tag_models=[tag_model,tag_joint_model]
    # tag_models=[tag_model,tag_model]
    tag_models=[None,None]
    pcfg_model=cPickle.load(file(pcfg_pickle_file,'r'))
    print 'test file:',tf
    senl=[x.strip().decode('utf8') for x in file(tf)]
    #senl=senl[60:61]
    res=[]
    i=0
    total_w_len=0
    total_c_len=0
    for asen in senl[:]:
        if len(asen)<1:
            continue
        t=read_tree(asen)
        wt=t.get_words()
        words=[x[0] for x in wt]
        total_w_len+=len(words)
        total_c_len+=len(''.join(words))
        wl=t.get_words()#[(word,pos),,,]
        new_t=CTB_parse_sen(wl,2,tag_models,pcfg_model)
        res.append(new_t[0][0].show())
        i+=1
        print i#,asen
    #######
    mean_w_len=total_w_len*1.0/len(senl)
    mean_c_len=total_c_len*1.0/len(senl)
    print '����ƽ������:'.decode('gbk'),mean_w_len
    print '����ƽ������:'.decode('gbk'),mean_c_len
    write_file(resf,res)
if __name__=='__main__':
    print time.asctime()
    begin_time=time.time()
    test_main(test_file,result_file)
    # #######
    # sentence='( (CP (CP (IP (NP (CP (IP (VP (ADVP (AD ����))(VP (VV ����)(NP (NN ����)))))(DEC ��))(NP (NN ��վ)))(VP (ADVP (AD δ��))(VP (VC ��)(VP (ADVP (AD ��))(VP (VA ����))))))(SP ��))(PU ��)) )'
    # t=CTB_main(psj=None, sen=sentence.decode('gbk'))
    # print t
    # for xt in t[0]:
    #     print xt[1],xt[0].show()+'\n###'
    # ####
    # tree = MultiTree()
    # tree.createTree(t[0].show())
    # writer = treeWriter(tree)
    # if len(sys.argv) > 1:#your graph file name
    #     outfile = sys.argv[1]
    #     writer.write(outfile) #write result to outfile
    # else:
    #     writer.write() #write result to tree.png
    # ####
    print time.asctime()
    print 'cost seconds:',time.time()-begin_time
    print 'done'
####
