# -*- coding: cp936 -*-
'''
target:CTB find split sen
author:hdz
time:2015-1-5 23:03:12
'''
import re
import cPickle
import copy
from CCG_tree import node,read_tree
max_len=5#5,6,7
version='_len_'+str(max_len)+'_BME'
test_file='files/ctb_8_test_right.txt'
res_file='files/ctb_8_test_right_split_res.txt'+version
piece_joint_file='files/ctb_8_test_right_split_joint.pickle'+version
res_crf_file='files/ctb_8_test_right_split_res_crf.txt'+version

_test_file='files/CTB_binary2.txt'
_res_file='files/CTB_binary2_split.txt'+version
_piece_joint_file='files/CTB_binary2_piece_joint.pickle'+version#for piece joint crf src file
_res_crf_file='files/CTB_binary2_split_crf.txt'+version
##
is_test=True
##is_test=False
split_pos=['PU']#
split_punc='�� �� �� �� �� '.decode('gbk').split(' ')
# crf_tag_list=[['S'],['B','E'],['B','B2','E'],\
#               ['B','B2','E2','E']]
crf_tag_list=[['S'],['B','E']]###MMEEEE
#����p:�ѱ��ý�
##nosplit_p='�� �� �� ��'.decode('gbk').split(' ')
##nosplit_c='�� �� �� �Լ� �� ���� ͬ'.decode('gbk').split(' ')
##split_verb='ʹ ��'.decode('gbk').split(' ')
#�ָ���,һЩ���۵Ķ���v+j
def write_file(fn,res):
    with open(fn,'w') as ff:
        ff.write('\n'.join(res).encode('utf8','ignore'))
    #print 'write done'
def piece_to_crf_data(src_file,res_file):
    '''�ѷֿ���ı�,����crf���
    (vp)\n(np)   
    '''
    def crf_str_add(aw,tag):
        return (aw[0],aw[1],tag)
    def tag_wl(wll):
        #B,B2,M,E2,E,S
        crf_str=[]
        lenth=len(wll)
        '''
        if lenth<=4:
            i=0
            for x in crf_tag_list[lenth-1]:
                crf_str.append(crf_str_add(wll[i],x))
                i+=1
        else:
            crf_str.append(crf_str_add(wll[0],'B'))
            crf_str.append(crf_str_add(wll[1],'B2'))
            for x in wll[2:-2]:
                crf_str.append(crf_str_add(x,'M'))
            crf_str.append(crf_str_add(wll[-2],'E2'))
            crf_str.append(crf_str_add(wll[-1],'E'))
        '''
        if lenth<=2:
            i=0
            for x in crf_tag_list[lenth-1]:
                crf_str.append(crf_str_add(wll[i],x))
                i+=1
        else:
            crf_str.append(crf_str_add(wll[0],'B'))
            for x in wll[1:-1]:
                crf_str.append(crf_str_add(x,'M'))
            crf_str.append(crf_str_add(wll[-1],'E'))#######MMMEEEE
        #'''
        crf_str=['\t'.join(x) for x in crf_str]
        return '\n'.join(crf_str)
    lines=[x.strip().decode('utf8') for x in file(src_file)]#[:10]
    res=[]
    i=0
    for line in lines:
        if len(line.strip())>0:
            t=read_tree(line)
            wl=t.get_words()
            #print wl
            tag_piece=tag_wl(wl)
            res.append(tag_piece)
        else:#end of sentence
            res.append('')
        i+=1
        if i%1000==0:
            print i
    write_file(res_file,res)
def check_is_single_leaf(t):
    if t.isleaf:
        return True
    elif len(t.son)==1:
        return check_is_single_leaf(t.son[0])
    return False
def tag_split(t):
    if check_is_single_leaf(t):
        #print 'root',t.word
        t.level=False
        return t
    for son in t.son:       #a not splitpunc son is leaf,return it
        if check_is_single_leaf(son):
            if son.tag in split_pos and\
                son.word in split_punc:
                continue
            else:           #no complex son
                #print son.word
                t.level=False
                return t
    t.son=[tag_split(son) for son in t.son]
    t.level=True
    return t
def check_lenth(nt):
    def check_tag_not_equal(t1,t2):
        tag1=t1.tag
        tag2=t2.tag
        tag1=tag1.split('-')[0].rstrip('*')
        tag2=tag2.split('-')[0].rstrip('*')
        return tag1!=tag2
    if len(nt.get_words())<=max_len:
        return [nt]
    ntl=[]
    if len(nt.son)==2:
        if check_tag_not_equal(nt.son[0],nt.son[1]) or len(nt.get_words())>=10:
            ntl.extend(check_lenth(nt.son[0]))
            ntl.extend(check_lenth(nt.son[1]))
        else:
            ntl.append(nt)
    elif len(nt.son)==1:
        ntl.extend(check_lenth(nt.son[0]))
    else:
        print '3 sons'
        for son in nt.son:
            ntl.extend(check_lenth(son))
    return ntl
def get_split_nodel(nt):
    nodel=[]
    if nt.level==False:
        nodel.append(nt)
    else:
        for son in nt.son:
            if son.level==False:
                # nodel.append(son)
                nodel.append(son)
            else:
                nodel.extend(get_split_nodel(son))
    return nodel
    # if nt.level==True or nt.isleaf:
    #     # nodel.append(nt)
    #     nodel.extend(check_lenth(nt))
    # else:
    #     for son in nt.son:
    #         if son.level==True or son.isleaf:
    #             # nodel.append(son)
    #             nodel.extend(check_lenth(son))
    #         else:
    #             nodel.extend(get_split_nodel(son))
    # return nodel
def split_main(t):#####������
    #nodel=[]
    nt=tag_split(t)
    nodel=get_split_nodel(nt)
    #print len(nodel)
    return nodel
def split_sen(fn,resf):
    lines=[x.strip().decode('utf8') for x in file(fn)]#[:1]
    res=[]
    i=0
    for line in lines:
        if len(line.strip())>0:
            t=read_tree(line)
            tl=split_main(t)
            for node in tl:
##                while not node.isleaf and len(node.son)==1:
##                    node=node.son[0]
                res.append(node.show())
            res.append('')
        i+=1
        if i%1000==0:
            print i
    write_file(resf,res)
########
def split_for_piece_joint_file(fn,resf):
    lines=[x.strip().decode('utf8') for x in file(fn)]
    res=[]
    i=0
    for line in lines:
        if len(line.strip())>0:
            t=read_tree(line)
            nt=tag_split(t)
            res.append(nt)
        i+=1
        if i%1000==0:
            print i
    cPickle.dump(res,file(resf,'wb'),True)
if __name__=='__main__':
    pass
    # split_sen(test_file,res_file)
    # split_for_piece_joint_file(test_file,piece_joint_file)
    # piece_to_crf_data(res_file,res_crf_file)
    #
    # split_sen(_test_file,_res_file)
    # split_for_piece_joint_file(_test_file,_piece_joint_file)
    # piece_to_crf_data(_res_file,_res_crf_file)
    # print 'done'
    sen=read_tree('( (IP (IP (NP-PN (NR ����))(VP (VV ���)(NP (CP (IP (VP (ADVP (AD ��ʷ����))(ADVP (AD ��))(VP (VA �Ͽ�))))(DEC ��))(NP (NN �ɺ�)))))(PU ��)(IP (NP (NP-PN (NR ����))(NP (NN �ڽ�)(NN ����)))(VP (NP (NT ����))(VP (VV ����)(NP (ADJP (JJ ȫ����))(NP (NN ����)(NN �))))))(PU ��)) )'.decode('gbk'))
    sen=read_tree('(IP (IP (IP (AD ����)(IP (VP (LCP (P ��)(LCP (NP (NN ����))(LC ��)))(FRAG (VV �⵽)(FRAG (NN �ͽ�)(NP (CC ��)(NN ����)))))))(IP (IP (PU ��)(IP (CC ����)(IP (IP (NP (NP (PN ����))(DEG ��))(IP (NN ����)(NP (CC ��)(NN �ɷ�))))(VP (VRD (VV ����)(VV Ҫ))(IP (VV �뿪)(NP (PN ����)))))))(IP (PU ��)(IP (IP (VP (NP (PN ����))(VP (ADVP (AD ��))(NP (NP (VV �˽�)(NP (IP (LCP (DP (DT ��))(NP (NN ����)))(LC ��))(NP (IP (ADVP (AD ����))(VP (VA �޺�)))(DEC ��))))(NP (NN ��Ϊ))))))(IP (PU ��)(VP (ADVP (AD ��))(VP (NP (P Ϊ)(NP (PN ����)))(NP (VV ����)(NP (NP (CD һ)(NP (ADJP (JJ ��))(CLP (M ��))))(NP (NN ����)))))))))))(PU ��))'.decode('gbk'))
    sen=read_tree('''
    ( (IP (NP-PN (NR ����))(VP (VV ��ʾ)(PU ��)(IP (NP (PN ��))(VP (VV ��Ϊ)(IP (NP (DP (DT ��)(CLP (M ��)))(NP (NN ȫ��))(NP (NN ����)(NN �)))(PU ��)(VP (VV ��ʾ)(IP (NP (NN ����)(NN ����))(VP (ADVP (AD ��))(VP (VV ��ʼ)(VP (VV �˽�)(PU ��)(NP (CP (IP (NP (NN �ɺ�))(VP (PP (P ��)(NP (NN ����)(NN ����)))(VP (MSP ��)(VP (VV ���)))))(DEC ��))(NP (NN ���))))))))))))(PU ��)) )
                  '''.decode('gbk'))
    ntl=split_main(sen)
    for st in ntl:
        print st.show()














    





