from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
import pandas as pd
import requests, time, re
from bs4 import BeautifulSoup, NavigableString
import time

# 사이트별 설정
sites_config = {
    'www_ytn_co_kr': {
        'date': ("div", "date"),
        'title': ("h2", "news_title"),
        'text': ("div", "paragraph"),
    },

}

sites_config_decompose = {
    'www_yna_co_kr': {
        'date': ("p", "update-time"),
        'title': ("h1", "tit"),
        'text': ("article", "story-news article"),
        'decompose': (['writer', 'desc', 'copyright', 'ad-box', 'tit-sub'])
    },

    'news_kbs_co_kr': {
        'date': ("div", {'class': "dates"}),
        'title': ("h4", {'class': "headline-title"}),
        'text': ("div", {'class': "detail-body"}),
        'decompose': (['view_img', 'badge', 'table'])
    },

    'news_sbs_co_kr': {
        'date': ("div", "date_area"),
        'title': ("h1", "article_main_tit"),
        'text': ("div", "text_area"),
        'decompose': (['strong', 'i_large', 'color:#0033ff']) # strong은 애매한듯
    },

    'www_peoplepowerparty_kr': {
        'date': ("dd", "date"),
        'title': ("dt", "sbj"),
        'text': ("dd", "conts"),
        'decompose': (['text-indent:-33.0pt;text-align:center;word-break:keep-all;margin-left:33.0pt;mso-pagination:none;text-autospace:none;mso-padding-alt:0.0pt 0.0pt 0.0pt 0.0pt;',
                       'text-align:center;word-break:keep-all;mso-pagination:none;text-autospace:none;mso-padding-alt:0.0pt 0.0pt 0.0pt 0.0pt;'
                       ]) # strong은 애매한듯
    },    

    'news_chosun_com': {
        'date': ("span", "inputDate"),
        'title': ("h1", "article-header__headline | font--secondary text--black"),
        'text': ("section", "article-body"),
        'decompose': (['figure']) # strong은 애매한듯
    },

    'www_hankookilbo_com': {
        'date': ("dl", "wrt-text"),
        'title': ("h1", "title"),
        'text': ("div", {"itemprop": "articleBody"}),
        'decompose': (['sub-tit', 'ttl', 'strong', 'figure', 'end-ad', 'report-banner', 'btn-area', 'editor-img', 'edit-subscribe', 'article-bottom', 'newspaper', 'script', 'more-articles', 'more-news', 'writer'])
    },

    'hankookilbo_com': {
        'date': ("dl", "wrt-text"),
        'title': ("h1", "title"),
        'text': ("div", {"itemprop": "articleBody"}),
        'decompose': (['sub-tit', 'ttl', 'strong', 'figure', 'end-ad', 'report-banner', 'btn-area', 'editor-img', 'edit-subscribe', 'article-bottom', 'newspaper', 'script', 'more-articles', 'more-news', 'writer'])
    },

    'theminjoo_kr': {
        'date': ("li", "date"),
        'title': ("h3", "tit"),
        'text': ("div", "board-view__contents"),
        'decompose': (['text-align: center; '])
    },

    'www_newsis_com': {
        'date': ("p", "txt"),
        'title': ("h1", "tit title_area"),
        'text': ("div", "viewer"),
        'decompose': (['summury', 'textBody', 'copyright'])
    },

    'radio_ytn_co_kr': {
        'date': ("th", "date"),
        'title': ("th", "title"),
        'text': ("td", {"colspan": "2", "style": "text-align:justify;line-height:1.7"}),
        'decompose': (['br'])
    },

    'news_kmib_co_kr': {
        'date': ("div", "date"),
        'title': ("h1", "article_headline"),
        'text': ("div", {'id': "articleBody"}),
        'decompose': (['figure', 'center'])
    },

    'www_munhwa_com': {
        'date': ("ul", "view_info_date"),
        'title': ("h1", "view_title"),
        'text': ("div", "article News_content"),
        'decompose': (['art_img', 'sub_title'])
    },

    'www_chosun_com': {
        'date': ("span", "dateBox"),
        'title': ("h1", "article-header__headline"),
        'text': ("section", "article-body"),
        'decompose': (['figure', 'a2'])
    },

    'www_ohmynews_com': {
        'date': ("div", "info_data"),
        'title': ("h3", "tit_subject"),
        'text': ("div", "at_contents"),
        'decompose': (['photoCenter'])
    },

    'omn_kr': {
        'date': ("div", "info_data"),
        'title': ("h3", "tit_subject"),
        'text': ("div", "at_contents"),
        'decompose': (['photoCenter'])
    },

    'www_yonhapnews_co_kr': {
        'date': ("p", "update-time"),
        'title': ("h1", "tit"),
        'text': ("article", "story-news article"),
        'decompose': (['writer', 'desc', 'copyright', 'ad-box', 'tit-sub'])
    },

    'www_mk_co_kr': {
        'date': ("div", "time_area"),
        'title': ("h2", "news_ttl"),
        'text': ("div", "news_cnt_detail_wrap"),
        'decompose': (['mid', 'img', 'ad_wrap', 'thumb_area'])
    },

    'biz_chosun_com': {
        'date': ("span", {'class': "dateBox"}),
        'title': ("h1", {'class': "article-header__headline"}),
        'text': ("section", {'class': "article-body"}),
        'decompose': (['strong', 'figure', 'arcad-wrapper'])
    },

    'www_sedaily_com': {
        'date': ("div", {'class': "article_info"}),
        'title': ("h1", {'class': "art_tit"}),
        'text': ("div", {'class': "article_view"}),
        'decompose': (['sub_ad', 'figure', 'art_rel', 'copy'])
    },

    'imnews_imbc_com': {
        'date': ("div", {'class': "date"}),
        'title': ("h2", {'class': "art_title"}),
        'text': ("div", {'class': "news_txt"}),
        'decompose': (['tit', 'figure', 'copy'])
    },

    'www_segye_com': {
        'date': ("p", {'class': "viewInfo"}),
        'title': ("h3", {'id': "title_sns"}),
        'text': ("article", {'class': "viewBox2"}),
        'decompose': (['precis', 'figure', 'copy'])
    },

    'www_koreaherald_com': {
        'date': ("h1", {'class': "news_title"}),
        'title': ("p", {'class': "news_date"}),
        'text': ("div", {'class': "view_con article"}),
        'decompose': (['img', 'copy'])
    },

    'news_khan_co_kr': {
        'date': ("div", {'class': "byline"}),
        'title': ("h1", {'class': "headline"}),
        'text': ("div", {'class': "art_body"}),
        'decompose': (['font', 'script', 'ads5PgPv', 'srch-kw', 'editor', 'photo', 'article_bottom_ad', 'caption', 'strapline'])
    },

    'www_khan_co_kr': {
        'date': ("div", {'class': "byline"}),
        'title': ("h1", {'class': "headline"}),
        'text': ("div", {'class': "art_body"}),
        'decompose': (['font', 'script', 'ads5PgPv', 'srch-kw', 'editor', 'photo', 'article_bottom_ad', 'caption', 'strapline'])
    },

    'h2_khan_co_kr': {
        'date': ("div", {'class': "byline"}),
        'title': ("h1", {'class': "headline"}),
        'text': ("div", {'class': "art_body"}),
        'decompose': (['font', 'script', 'ads5PgPv', 'srch-kw', 'editor', 'photo', 'article_bottom_ad', 'caption', 'strapline'])
    },

    'news_mk_co_kr': {
        'date': ("div", {'class': "time_area"}),
        'title': ("h2", {'class': "news_ttl"}),
        'text': ("div", {'class': "news_cnt_detail_wrap"}),
        'decompose': (['mid_title', 'ad_wrap'])
    },

    'www_fnnews_com': {
        'date': ("span", {'class': "row-2"}),
        'title': ("h1", {'class': "tit_thumb"}),
        'text': ("div", {'class': "cont_view"}),
        'decompose': (['summary', 'view_', 'customByline', 'rt_issue', 'taboola-below', 'script', 'newsStand'])
    },

    'www_dt_co_kr': {
        'date': ("div", {'class': "article_info"}),
        'title': ("h1", {'class': "art_tit"}),
        'text': ("div", {'class': "article_view"}),
        'decompose': (['img_', 'article_copy'])
    },

    'news_heraldcorp_com': {
        'date': ("li", {'class': "article_date"}),
        'title': ("li", {'class': "article_title ellipsis2"}),
        'text': ("div", {'class': "article_view"}),
        'decompose': (['img', 'article_copy', 'strong', 'summary', 'margin-bottom', 'ad_area'])
    },

    'koreajoongangdaily_joins_com': {
        'date': ("a", {'class': "article-publish-date"}),
        'title': ("h1", {'class': "view-article-title serif"}),
        'text': ("div", {'id': "article_body"}),
        'decompose': (['ab_photo', 'artAd', 'view-article-title'])
    },

    'www_etnews_com': {
        'date': ("time", {'class': "date"}),
        'title': ("div", {'class': "article_title"}),
        'text': ("div", {'class': "article_txt"}),
        'decompose': (['figure', 'footer_btnwrap'])
    },

    'www_busan_com': {
        'date': ("div", {'class': "byline"}),
        'title': ("p", {'class': "title"}),
        'text': ("div", {'class': "article_content"}),
        'decompose': (['subtitle', 'img_', 'wcms_ad', 'text-', 'div-gpt-ad'])
    },

    'www_kwnews_co_kr': {
        'date': ("span", {'class': "date"}),
        'title': ("h2", {'class': "title"}),
        'text': ("div", {'id': "articlebody"}),
        'decompose': (['figure', 'art_mid_ad'])
    },

    'www_daejonilbo_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'ad-view'])
    },

    'www_kado_net': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'ad-view'])
    },

    'www_imaeil_com': {
        'date': ("span", {'class': "date"}),
        'title': ("h1", {'class': "title"}),
        'text': ("div", {'id': "articlebody"}),
        'decompose': (['figure', 'art_mid_ad'])
    },

    'biz_heraldcorp_com': {
        'date': ("li", {'class': "article_date"}),
        'title': ("li", {'class': "article_title ellipsis2"}),
        'text': ("div", {'class': "article_view"}),
        'decompose': (['figure', 'strong', 'img'])
    },

    'www_kyeonggi_com': {
        'date': ("div", {'class': "article_date"}),
        'title': ("h1", {'class': "article_tit"}),
        'text': ("div", {'class': "article_cont_wrap"}),
        'decompose': (['sub_tit', 'input', 'report_box', 'figure', 'center_ad', 'btm_ad', 'tag_', 'mb30', 'borderT', 'script'])
    },

    'decenter_sedaily_com': {
        'date': ("div", {'class': "article_info"}),
        'title': ("h2", ),
        'text': ("div", {'class': "view_con"}),
        'decompose': (['info_reporter', 'article_copy'])
    },

    'www_kmib_co_kr': {
        'date': ("span", {'class': "t11"}),
        'title': ("h1", {'class': "article_headline"}),
        'text': ("div", {'class': "tx"}),
        'decompose': (['figure', 'article_copy'])
    },

    'www_newdaily_co_kr': {
        'date': ("div", {'class': "article-date"}),
        'title': ("h1", ),
        'text': ("div", {'id': "article_conent"}),
        'decompose': (['center_img', 'script', 'iwmads'])
    },

    'www_fntoday_co_kr': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['view-editor', 'view-copyright', 'style', 'color:#8e44ad;', 'text-align:center', 'main-bt', 'support', 'info-options', 'clear'])
    },

    'news_jtbc_joins_com': {
        'date': ("span", {'class': "artical_date"}),
        'title': ("h3", {'id': "jtbcBody"}),
        'text': ("div", {'class': "article_content"}),
        'decompose': (['article_list_wrap', 'jtbc_vod'])
    },

    'www_insight_co_kr': {
        'date': ("div", {'class': "news-read-header-info-date"}),
        'title': ("div", {'class': "news-read-header-title"}),
        'text': ("div", {'class': "news-read-content-memo"}),
        'decompose': (['image',])
    },

    'www_joongboo_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure',])
    },

    'www_justice21_org': {
        'date': ("span", {'class': "date subject"}),
        'title': ("li", {'class': "subject"}),
        'text': ("div", {'class': "content"}),
        'decompose': (['strong'])
    },

    'news_tvchosun_com': {
        'date': ("p", {'class': "date"}),
        'title': ("h3", {'class': "title"}),
        'text': ("div", {'class': "article_detail_body"}),
        'decompose': (['vod_player', 'article_sub_title'])
    },

    'www_peoplepower21_org': {
        'date': ("small", {'class': "text-muted"}),
        'title': ("span", {'id': "post_title"}),
        'text': ("div", {'id': "container_write"}),
        'decompose': (['href', 'li', 'cosmosfarm', 'color:', 'script', 'h2', 'py-3'])
    },

    'www_newspim_com': {
        'date': ("div", {'class': "writetime"}),
        'title': ("h2", {'id': "main-title"}),
        'text': ("div", {'id': "news-contents"}),
        'decompose': (['table'])
    },

    'www_dailian_co_kr': {
        'date': ("div", {'class': "divtext2"}),
        'title': ("h1", {'class': "title"}),
        'text': ("div", {'class': "article"}),
        'decompose': (['flex flex', 'inner-sub', 'figure', 'copyright', 'script'])
    },

    'www_businesspost_co_kr': {
        'date': ("div", {'class': "author_info"}),
        'title': ("h2", ),
        'text': ("div", {'class': ["detail_tab_cont", "detail_editor"]}),
        'decompose': (['figure', 'copyright', 'script'])
    },

    'www_mediatoday_co_kr': {
        'date': ("div", {'class': "user-info"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'class': "article-veiw-body view-page font-size19"}),
        'decompose': (['style', 'figure', 'copyright', 'script'])
    },

    'www_etoday_co_kr': {
        'date': ("div", {'class': "newsinfo"}),
        'title': ("h1", {'class': "main_title"}),
        'text': ("div", {'class': "articleView"}),
        'decompose': (['width:600px;margin:auto;text-align', 'figure', 'copyright', 'script'])
    },

    'www_ajunews_com': {
        'date': ({'class': "date"}),
        'title': ("h1", ),
        'text': ("div", {'class': "article_con"}),
        'decompose': (['dcamp_ad', 'byline', 'script', 'like_wrap', 'article_bot', 'figure', 'copy'])
    },

    'www_breaknews_com': {
        'date': ("div", {'class': "writer_time"}),
        'title': ("h1", {'class': "read_title"}),
        'text': ("div", {'id': "CLtag"}),
        'decompose': (['script', 'figure', 'copy'])
    },

    'news_tf_co_kr': {
        'date': ("div", {'class': "timeTxt"}),
        'title': ("div", {'class': "articleTitle"}),
        'text': ("div", {'class': "article"}),
        'decompose': (['tbody', 'strong', 'script', 'figure', 'copy'])
    },

    'www_newstomato_com': {
        'date': ("div", {'class': "rn_sdate"}),
        'title': ("div", {'class': "rn_stitle"}),
        'text': ("div", {'class': "rns_text"}),
        'decompose': (['text-align: justify;', 'desc', 'display', 'script', 'figure', 'copy'])
    },

    'shindonga_donga_com': {
        'date': ("span", {'class': "time"}),
        'title': ("p", {'class': "title_text"}),
        'text': ("div", {'class': "article_view"}),
        'decompose': (['postscript', 'desc', 'article_photo', 'script', 'figure', 'copy'])
    },

    'www_sisajournal_com': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title title-cus"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['article_replay', 'viewreply', 'box-skin', 'view-editor', 'view-copy', 'tag-group', 'article-head', 'article-sns', 'article-tool', 'script', 'figure'])
    },

    'www_inews24_com': {
        'date': ("time", {'datetime'}),
        'title': ("h1", ),
        'text': ("article", {'class': "view font16"}),
        'decompose': (['author-list', 'address', 'script', 'figure'])
    },

    'www_moneys_co_kr': {
        'date': ("div", {'class': "date"}),
        'title': ("h1", {'class': "title"}),
        'text': ("div", {'class': "article-body font-size-5"}),
        'decompose': (['article_photo', 'script', 'figure'])
    },

    'www_polinews_co_kr': {
        'date': ("ul", {'class': "article-info-label"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['ad-view', 'style', 'script', 'figure'])
    },

    'www_gukjenews_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['ad-view', 'style', 'script', 'figure'])
    },

    'yna_kr': {
        'date': ("p", {'class': "update-time"}),
        'title': ("h1", {'class': "tit"}),
        'text': ("article", {'class': "story-news article"}),
        'decompose': (['txt-copyright', 'aside-', 'tit-sub', 'newsWriter', 'style', 'script', 'figure'])
    },

    'news_jtbc_co_kr': {
        'date': ("span", {'class': "i_date"}),
        'title': ("h3", {'id': "jtbcBody"}),
        'text': ("div", {'class': "article_content"}),
        'decompose': (['txt-copyright', 'jtbc_vod', 'tit-sub', 'newsWriter', 'style', 'script', 'figure'])
    },

    'www_skyedaily_com': {
        'date': ("font", {'class': "articledata"}),
        'title': ("div", {'class': "bigtitle"}),
        'text': ("div", {'class': "articletext2"}),
        'decompose': (['txt-copyright', 'jtbc_vod', 'tit-sub', 'newsWriter', 'style', 'script', 'figure'])
    },

    'www_safetimes_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'class': "article-veiw-body view-page font-size17"}),
        'decompose': (['tit-sub', 'script', 'figure'])
    },

    'www_christiantoday_co_kr': {
        'date': ("div", {'class': "byline"}),
        'title': ("h1", ),
        'text': ("div", {'class': "article-body clearfix"}),
        'decompose': (['table', 'tit-sub', 'script', 'figure'])
    },

    'www_ekn_kr': {
        'date': ("span", {'class': "none"}),
        'title': ("h1", {'class': "view-main-title"}),
        'text': ("div", {'class': "view-text"}),
        'decompose': (['article_view_byline', 'article-photo', 'table', 'tit-sub', 'script', 'figure'])
    },
    
    'www_newsfreezone_co_kr': {
        'date': ("ul", {'class': "article-info-label"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['style', 'table', 'ad-view', 'script', 'figure'])
    },

    'www_joongdo_co_kr': {
        'date': ("ul", {'class': "view-term"}),
        'title': ("h1", {'class': "v-title1"}),
        'text': ("div", {'id': "font"}),
        'decompose': (['style', 'table', 'ad-view', 'script', 'figure'])
    },

    'weekly_chosun_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['style', 'table', 'ad-view', 'script', 'figure'])
    },

    'www_kukinews_com': {
        'date': ("span", {'class': "date"}),
        'title': ("h1", {'class': "view-title"}),
        'text': ("div", {'id': "article"}),
        'decompose': (['view-footer', 'more_link', 'style', 'table', 'ad-view', 'script', 'figure'])
    },

    'www_newscj_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['relation', 'style', 'table', 'ad-view', 'script', 'figure'])
    },

    'www_yonhapnewstv_co_kr': {
        'date': ("ul", {'class': "info"}),
        'title': ("strong", {'class': "title"}),
        'text': ("div", {'id': "articleBody"}),
        'decompose': (['videoWrap', 'table', 'script', 'figure'])
    },

    'zdnet_co_kr': {
        'date': ("p", {'class': "meta"}),
        'title': ("h1", ),
        'text': ("div", {'class': "view_cont"}),
        'decompose': (['mt_bn_box', 'margin:0px; font-weight:bold;', 'videoWrap', 'table', 'script', 'figure'])
    },

    'daily_hankooki_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['ad-view', 'style', 'script', 'figure'])
    },

    'www_ichannela_com': {
        'date': ("span", {'class': "date"}),
        'title': ("strong", {'class': "title"}),
        'text': ("div", {'class': "news_page_txt"}),
        'decompose': (['ad-view', 'style', 'script', 'figure'])
    },

    'www_metroseoul_co_kr': {
        'date': ("div", {'class': "info-byline-container"}),
        'title': ("h1", {'class': "detail-title"}),
        'text': ("div", {'class': "row article-txt-contents"}),
        'decompose': (['ad-view', 'style', 'script', 'figure'])
    },

    'www_labortoday_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['ad-view', 'style', 'script', 'figure'])
    },

    'www_viva100_com': {
        'date': ("p", {'class': "view_top_days view1_top_days"}),
        'title': ("h1", {'class': "view_top_title"}),
        'text': ("div", {'class': "left_text_box"}),
        'decompose': (['gija_gisa', 'tbody', 'ad-view', 'style', 'script', 'figure'])
    },

    'www_pennmike_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['tbody', 'ad-view', 'style', 'script', 'figure'])
    },

    'ilyo_co_kr': {
        'date': ("div", {'class': "actInfo"}),
        'title': ("h2", {'class': "atcTitle"}),
        'text': ("div", {'class': "contentView"}),
        'decompose': (['actPhoto', 'ad-view', 'style', 'script'])
    },

    'h21_hani_co_kr': {
        'date': ("div", {'class': "arti-date toggle"}),
        'title': ("h2", {'class': "arti-tit"}),
        'text': ("div", {'class': "arti-txt"}),
        'decompose': (['strong', 'bn-promotion', 'photo-box', 'ad-box', 'style', 'script'])
    },

    'www_wikitree_co_kr': {
        'date': ("p", {'class': "date_time"}),
        'title': ("h1", {'id': "article"}),
        'text': ("div", {'id': "wikicon"}),
        'decompose': (['strong', 'figure', 'ad-box', 'style', 'script'])
    },

    'www_mediapen_com': {
        'date': ("div", {'class': "date-repoter"}),
        'title': ("div", {'class': "title"}),
        'text': ("div", {'class': "article-body-content"}),
        'decompose': (['table', 'figure', 'style', 'script'])
    },

    'www_topstarnews_net': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("h1", {'class': "article-head-title"}),
        'text': ("div", {'class': "article-view-page clearfix"}),
        'decompose': (['copyright', 'ad-view', 'writer account', 'figure', 'style', 'script'])
    },

    'www_asiatime_co_kr': {
        'date': ("p", {'class': "article_byline"}),
        'title': ("h6", ),
        'text': ("div", {'class': "row article_txt_container"}),
        'decompose': (['copyright', 'ad_', 'summary', 'figure', 'style', 'script'])
    },

    'biz_sbs_co_kr': {
        'date': ("div", {'class': "ah_info"}),
        'title': ("h3", {'class': "ah_big_title"}),
        'text': ("div", {'class': "article_body"}),
        'decompose': (['text-align: center;', 'ab_image', 'ab_reporter', 'article_copy', 'ab_video', 'summary', 'figure', 'style', 'script'])
    },

    'www_shinailbo_co_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['byline', 'margin-top:-20px;', 'head-sub', 'editors', 'copyright', 'figure', 'style', 'script'])
    },

    'www_wowtv_co_kr': {
        'date': ("p", {'class': "date-news"}),
        'title': ("h1", {'class': "title-news"}),
        'text': ("div", {'class': "box-news-body"}),
        'decompose': (['copyright', 'figure', 'style', 'script'])
    },

    'www_kyeongin_com': {
        'date': ("span", {'class': "news-date"}),
        'title': ("h1", {'class': "news-title"}),
        'text': ("div", {'class': ["view_txt clearfix paper-article-view", 'view_txt clearfix']}),
        'decompose': (['tag_news', 'table', 'view_byline', 'copyright', 'article-photo', 'style', 'script'])
    },

    'www_namdonews_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['copyright', 'figure', 'style', 'script'])
    },

    'www_naeil_com': {
        'date': ("span", {'class': "date"}),
        'title': ("h1", {'class': "headline"}),
        'text': ("div", {'class': "article-view-main"}),
        'decompose': (['major-news', 'reporter-news-more', 'subtitle', 'copyright', 'figure', 'style', 'script'])
    },

    'www_ggilbo_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['copyright', 'figure', 'style', 'script'])
    },

    'www_voakorea_com': {
        'date': ("span", {'class': "date"}),
        'title': ("h1", {'class': "title pg-title"}),
        'text': ("div", {'class': "wsw"}),
        'decompose': (['wsw__embed', 'copyright', 'figure', 'style', 'script'])
    },

    'kormedi_com': {
        'date': ("span", {'class': "time meta_web"}),
        'title': ("span", {'class': "post-title"}),
        'text': ("div", {'class': "single-container"}),
        'decompose': (['post-header', 'author', 'recommend', 'bsac bsac', 'related', 'copyright', 'figure', 'style', 'script'])
    },

    'www_tongilnews_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['table', 'copyright', 'figure', 'style', 'script'])
    },

    'www_dnews_co_kr': {
        'date': ("div", {'class': "dateFont"}),
        'title': ("div", {'class': "title"}),
        'text': ("div", {'class': "text"}),
        'decompose': (['strong', 'table', 'copyright', 'figure', 'style', 'script'])
    },

    'www_g-enews_com': { 
        'date': ("p", {'class': "r3"}),
        'title': ("h1", ),
        'text': ("div", {'class': "vtxt detailCont"}),
        'decompose': (['table', 'copyright', 'figure', 'style', 'script'])
    },
 
    'news_koreadaily_com': {  
        'date': ("p", {'class': "date-bold article-date-bold"}),
        'title': ("h1", {'class': "view-article-title"}),
        'text': ("div", {'class': "article_body fs4"}),
        'decompose': (['article-tag', 'ab_photo', 'ab_sub', 'view-', 'copyright', 'figure', 'style', 'script'])
    },

    'www_dongascience_com': { 
        'date': ("div", {'class': "info"}),
        'title': ("h2", ),
        'text': ("div", {'id': "article_body"}),
        'decompose': (['strong', 'pic_c'])
    },

    'autotimes_hankyung_com': {
        'date': ("p", {'class': "report_timedata"}),
        'title': ("h2", ),
        'text': ("div", {'class': "view_report"}),
        'decompose': (['strong', 'font', 'table', 'copyright', 'style', 'script'])
    },

    'www_nspna_com': {
        'date': ("div", {'class': "news_publish"}),
        'title': ("h2", {'class': "news_title"}),
        'text': ("div", {'class': "news_body"}),
        'decompose': (['epilog', 'ad_', 'byline', 'section_img', 'epilog', 'copyright', 'style', 'script'])
    },

    'www_thisisgame_com': {
        'date': ("span", {'class': "reporter-data"}),
        'title': ("h1", ),
        'text': ("div", {'class': "content board-content common-news-content"}),
        'decompose': (['ad_new', 'other-people', 'social-box', 'img', 'text-align: center;', 'copyright', 'style', 'script'])
    },

    'star_ytn_co_kr': {
        'date': ("div", {'class': "date"}),
        'title': ("h2", {'class': "news_title"}),
        'text': ("div", {'class': "paragraph"}),
        'decompose': (['copyright', 'style', 'script'])
    },

    'www_obsnews_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['ad-view', 'myVideo', 'copyright', 'style', 'script'])
    },

    'www_joseilbo_com': {
        'date': ("div", {'class': "news_reg_time"}),
        'title': ("h1", ),
        'text': ("div", {'class': "viewpage_txt"}),
        'decompose': (['caption', 'subtle', 'copyright', 'style', 'script'])
    },

    'www_bntnews_co_kr': {
        'date': ("div", {'class': "date"}),
        'title': ("h1", {'class': "title"}),
        'text': ("div", {'class': "content"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'www_sisain_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['article-view-sns', 'article-copy', 'tag-group', 'press', 'figure', 'style', 'script'])
    },

    'sports_khan_co_kr': {
        'date': ("div", {'class': "byline"}),
        'title': ("h1", {'class': "tit_head"}),
        'text': ("div", {'class': "art_body"}),
        'decompose': (['art_photo', 'figure', 'style', 'script'])
    },

    'www_sisaon_co_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['wrProfile', 'copyright', 'tag-group', 'tem-type-', 'head-sub', 'figure', 'style', 'script'])
    },

    'www_enewstoday_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'www_kgnews_co_kr': {
        'date': ("ul", {'class': "art_info"}),
        'title': ("h2", ),
        'text': ("div", {'id': "news_body_area"}),
        'decompose': (['imgframe', 'style', 'script'])
    },

    'weekly_khan_co_kr': {
        'date': ("div", {'class': "article_date"}),
        'title': ("div", {'class': "title edt190509"}),
        'text': ("div", {'class': "article_txt"}),
        'decompose': (['subtitle', 'art_photo', 'style', 'script'])
    },

    'www_seoulfn_com': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['strong', 'view-editors', 'view-copyright', 'head-sub', 'figure', 'style', 'script'])
    },

    'www_jbnews_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['tem-type', 'figure', 'style', 'script'])
    },

    'economist_co_kr': {
        'date': ("div", {'class': "article-menu-box"}),
        'title': ("h1", {'class': "view-article-title"}),
        'text': ("div", {'class': "content"}),
        'decompose': (['tem-type', 'figure', 'style', 'script'])
    },

    'www_kpinews_kr': {
        'date': ("div", {'class': "viewTitle"}),
        'title': ("h3", ),
        'text': ("div", {'class': "viewConts"}),
        'decompose': (['summary_title', 'figure', 'style', 'script', 'blockquote','color:#494949; font-size:14px;'])
    },

    'news_cpbc_co_kr': {
        'date': ("div", {'class': "ah_info"}),
        'title': ("h3", {'class': "ah_big_title"}),
        'text': ("div", {'class': "article_body"}),
        'decompose': (['figure', 'style', 'script','ab_reporter','ab_share', 'article_copy'])
    },

    'magazine_hankyung_com': {
        'date': ("div", {'class': "date-info"}),
        'title': ("h1", {'class': "news-tit"}),
        'text': ("div", {'class': "article-body"}),
        'decompose': (['figure', 'style', 'script','strong'])
    },

    'www_incheonilbo_com': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['emoji', 'writer_info', 'copyright', 'figure', 'style', 'script','strong'])
    },

    'www_greened_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['head-sub', 'tag-group', 'auto-martop', 'relation', 'editors', 'padding','copyright', 'figure', 'style', 'script'])
    },

    'www_domin_co_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['head-sub', 'tag-group', 'auto-martop', 'relation', 'editors', 'padding','copyright', 'figure', 'style', 'script'])
    },

    'news_mtn_co_kr': {
        'date': ("div", {'class': "css-1b8sprk"}),
        'title': ("h1", ),
        'text': ("div", {'class': "css-16jbccu"}),
        'decompose': (['table', 'copyright', 'figure', 'style', 'script'])
    },

    'www_newsmp_com': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['editors', 'strong', 'copyright', 'figure', 'style', 'script'])
    },

    'www_kmaeil_com': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['tag-group', 'head-sub', 'editors', 'copyright', 'figure', 'style', 'script'])
    },

    'biz_newdaily_co_kr': {  
        'date': ("div", {'class': "article-date"}),
        'title': ("div", {'class': "article-header"}),
        'text': ("div", {'id': "article_conent"}),
        'decompose': (['copyright', 'center_img', 'style', 'script'])
    },

    'www_getnews_co_kr': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['copyright', 'figure', 'style', 'script'])
    },

    'www_siminilbo_co_kr': {  
        'date': ("div", {'class': "viewTitle"}),
        'title': ("h3", ),
        'text': ("div", {'class': "viewConts"}),
        'decompose': (['color:#494949; font-size:14px;', 'copyright', 'figure', 'style', 'script'])
    },

    'news_bbsi_co_kr': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['strong', 'font-size:12px; cursor:pointer;', 'flowplayer', 'copyright', 'figure', 'style', 'script'])
    },  # strong은 애매함

    'www_danbinews_com': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['copyright', 'figure', 'style', 'script'])
    }, 

    'www_mediaus_co_kr': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['color:#e74c3c;', 'copyright', 'figure', 'style', 'script'])
    }, 

    'www_hansbiz_co_kr': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['email', 'copyright', 'figure', 'style', 'script'])
    }, 

    'www_laborplus_co_kr': {  
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['head-sub', 'editors', 'email', 'copyright', 'figure', 'style', 'script'])
    }, 

    'www_newstnt_com': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['head-sub', 'email', 'copyright', 'figure', 'style', 'script'])
    }, 

    'www_gjdream_com': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['color:#994C00;', 'email', 'copyright', 'figure', 'style', 'script'])
    }, 

    'www_hidomin_com': {  
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['head-sub', 'editors', 'email', 'copyright', 'figure', 'style', 'script'])
    }, 

    'www_fntimes_com': {  
        'date': ("div", {'class': "vcon_hd_din3"}),
        'title': ("h1", ),
        'text': ("div", {'class': "vcon_con_intxt"}),
        'decompose': (['head-sub', 'editors', 'font-size:14px;', 'copyright', 'mimg', 'style', 'script'])
    }, 

    'www_ksilbo_co_kr': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['head-sub', 'copyright', 'figure', 'style', 'script'])
    }, 

    'app_yonhapnews_co_kr': {  
        'date': ("p", {'class': "update-time"}),
        'title': ("h1", {'class': "tit"}),
        'text': ("article", {'class': "story-news article"}),
        'decompose': (['ad-box', 'aside-bnr', 'tit-sub', 'copyright', 'figure', 'style', 'script'])
    }, 

    'www_kyongbuk_co_kr': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['ad-box', 'copyright', 'figure', 'style', 'script'])
    }, 

    'www_sisafocus_co_kr': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['ad-box', 'copyright', 'figure', 'style', 'script'])
    }, 

    'www_dailypharm_com': {  
        'date': ("span", {'class': "d_newsDate"}),
        'title': ("div", {'class': "d_newsTitle"}),
        'text': ("div", {'class': "newsContents font1"}),
        'decompose': (['NewsBodyimg', 'copyright', 'figure', 'style', 'script'])
    }, 

    'realty_chosun_com': {  
        'date': ("p", {'id': "date_text"}),
        'title': ("h1", {'id': "news_title_text_id"}),
        'text': ("div", {'id': "news_body_id"}),
        'decompose': (['background:white', 'content_in_ad', 'ad_new', 'related', 'news_img', 'subtitle', 'news_date', 'copyright', 'figure', 'style', 'script'])
    }, 

    'www_goodmorningcc_com': {  
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['editors', 'tag-group', 'emoji', 'copyright', 'figure', 'style', 'script'])
    }, 

    'www_womennews_co_kr': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['copyright', 'figure', 'style', 'script'])
    }, 

    'www_sportsseoul_com': {  
        'date': ("div", {'class': "datetime"}),
        'title': ("h1", {'class': "headline"}),
        'text': ("div", {'id': "article-body"}),
        'decompose': (['subtitle', 'article-like', 'tbody', 'copyright', 'figure', 'style', 'script'])
    },

    'www_bbc_com': {  
        'date': ("li", {'class': "bbc-v8pmqw"}),
        'title': ("h1", {'id': "content"}),
        'text': ("main", {'class': "bbc-fa0wmp"}),
        'decompose': (['section', 'bbc-1151pbn ebmt73l0', 'copyright', 'figure', 'style', 'script'])
    },

    'weekly_hankooki_com': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['tag-group', 'tbody', 'subheading', 'copyright', 'figure', 'style', 'script'])
    },

    'www_ngonews_kr': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['tag-group', 'tbody', 'subheading', 'copyright', 'figure', 'style', 'script'])
    },

    'www_ccdn_co_kr': {  
        'date': ("ul", {'class': "article-info-label"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['tag-group', 'tbody', 'subheading', 'copyright', 'figure', 'style', 'script'])
    },

    'www_jjan_kr': {  
        'date': ("div", {'class': "byline_info_wrap"}),
        'title': ("h1", ),
        'text': ("div", {'class': "article_txt_container"}),
        'decompose': (['taboola', 'reply', '_ad', 'social', 'reporter', 'relation', 'series', 'tbody', 'subheading', 'copy', 'figure', 'style', 'script'])
    },

    'www_osen_co_kr': {  
        'date': ("div", {'class': "view-info__date"}),
        'title': ("strong", {'class': "view-info_title"}),
        'text': ("div", {'id': "articleBody"}),
        'decompose': (['center', 'copy', 'figure', 'style', 'script'])
    },

    'www_jeonmae_co_kr': {  
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("article", {'class': "article-veiw-body view-page font-size17"}),
        'decompose': (['editors', 'head-sub', 'copy', 'figure', 'style', 'script'])
    },

    'www_4th_kr': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['editors', 'head-sub', 'copy', 'figure', 'style', 'script'])
    },

    'www_sisunnews_co_kr': {  
        'date': ("ul", {'class': "article-info-label no-bullet"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("div", {'class': "cont-body"}),
        'decompose': (['editors', 'head-sub', 'copy', 'figure', 'style', 'script'])
    },

    'www_ilyoseoul_co_kr': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['strong', 'editors', 'head-sub', 'copy', 'figure', 'style', 'script'])
    },

    'www_huffingtonpost_kr': {  
        'date': ("ul", {'class': "infomation font-nanum"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['strong', 'editors', 'head-sub', 'copy', 'figure', 'style', 'script'])
    },

    'www_bosa_co_kr': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['strong', 'editors', 'head-sub', 'copy', 'figure', 'style', 'script'])
    },

    'vop_co_kr': {  
        'date': ("ul", {'class': "view_top_info"}),
        'title': ("h1", {'class': "view_top_tit"}),
        'text': ("div", {'class': "editor"}),
        'decompose': (['strong', 'editors', 'head-sub', 'copy', 'figure', 'style', 'script'])
    },

    'sjbnews_com': {  
        'date': ("div", {'class': "container p-t-4 p-b-35"}),
        'title': ("h3", {'class': "news_title cl2 p-b-16 p-t-33 respon2"}),
        'text': ("span", {'class': "news_text cl6 p-b-25"}),
        'decompose': (['strong', 'editors', 'copy', 'wrap-pic', 'style', 'script'])
    },

    'www_m-i_kr': {  
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['strong', 'editors', 'copy', 'wrap-pic', 'style', 'script'])
    },

    'health_chosun_com': {  
        'date': ("div", {'class': "h_info"}),
        'title': ("h1", {'class': "h_title"}),
        'text': ("div", {'id': "news_body_id"}),
        'decompose': (['relArt', 'strong', 'btn-area', 'copy', 'figure', 'style', 'script'])
    },

    'sports_chosun_com': {  
        'date': ("span", {'class': "article-day"}),
        'title': ("h1", {'class': "article-title"}),
        'text': ("div", {'class': "news_text"}),
        'decompose': (['strong', 'tbody', 'copy', 'figure', 'style', 'script'])
    },

    'www_lecturernews_com': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['strong', 'tbody', 'copy', 'figure', 'style', 'script'])
    },

    'www_inews365_com': {  
        'date': ("div", {'class': "art_sum"}),
        'title': ("h2", ),
        'text': ("div", {'id': "news_body_area"}),
        'decompose': (['strong', 'tbody', 'copy', 'img_box', 'style', 'script'])
    },

    'news_einfomax_co_kr': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['font-weight:bold; background-color:#EDEDED; padding:10px;', 'strong', 'tbody', 'copy', 'figure', 'style', 'script'])
    },

    'www_lawtimes_co_kr': {  
        'date': ("div", {'class': "css-1vaapo e179ozeo5"}),
        'title': ("div", {'class': "css-v1qkh e16ienf60"}),
        'text': ("div", {'class': "css-ipsxml e1ogx6dn0"}),
        'decompose': (['strong', 'tbody', 'copy', 'figure', 'style', 'script'])
    },

    'news_unn_net': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['strong', 'tbody', 'copy', 'figure', 'style', 'script'])
    },

    'www_newsworks_co_kr': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['strong', 'tbody', 'copy', 'figure', 'style', 'script'])
    },

    'www_yeongnam_com': {  
        'date': ("li", {'class': "article-bottom-input"}),
        'title': ("h1", {'class': "article-top-title"}),
        'text': ("div", {'class': "article-news-body font-size03"}),
        'decompose': (['text-align:center;', 'reporter', 'strong', 'tbody', 'copy', 'figure', 'style', 'script'])
    },

    'www_dynews_co_kr': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['strong', 'tbody', 'copy', 'figure', 'style', 'script'])
    },

    'www_ksmnews_co_kr': {  
        'date': ("div", {'class': "view_head_info_date"}),
        'title': ("div", {'class': "view_head_title"}),
        'text': ("div", {'id': "view_content_body"}),
        'decompose': (['summary', 'figure', 'blockquote', ])
    },

    'www_kjdaily_com': {  
        'date': ("ul", {'id': "byline"}),
        'title': ("div", {'class': "adttl"}),
        'text': ("div", {'id': "content"}),
        'decompose': (['font', 'tbody', 'summary', 'figure', 'blockquote', ])
    },

    'www_xportsnews_com': {  
        'date': ("div", {'class': "at_header"}),
        'title': ("h1", {'class': "at_title"}),
        'text': ("div", {'class': "news_contents"}),
        'decompose': (['iframe', 'tb top', 'tbody', 'summary', 'figure', 'script'])
    },

    'www_medicaltimes_com': {  
        'date': ("div", {'class': "date_info"}),
        'title': ("h3", {'id': "NewsTitle"}),
        'text': ("div", {'class': "view_cont ck-content clearfix"}),
        'decompose': (['iframe', 'tbody', 'summary', 'figure', 'script'])
    },

    'moneys_mt_co_kr': {  
        'date': ("div", {'class': "date"}),
        'title': ("h1", {'class': "title"}),
        'text': ("div", {'class': "article-body font-size-5"}),
        'decompose': (['ADVERTISE', 'tbody', 'figure', 'script'])
    },

    'www_bzeronews_com': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['ADVERTISE', 'tbody', 'figure', 'script'])
    },

    'www_incheontoday_com': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['ADVERTISE', 'tbody', 'figure', 'script'])
    },

    'www_cctoday_co_kr': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['ad-view', 'style', 'tbody', 'figure', 'script'])
    },

    'www_nongmin_com': {  
        'date': ("div", {'class': "inr"}),
        'title': ("pre", ),
        'text': ("div", {'class': "news_txt ck-content"}),
        'decompose': (['strong', 'ad-view', 'style', 'tbody', 'figure', 'script'])
    },

    'www_taxtimes_co_kr': {  
        'date': ("ul", {'class': "art_info"}),
        'title': ("h2", ),
        'text': ("div", {'id': "news_body_area"}),
        'decompose': (['font-size:14px;', 'imgframe', 'ad-view', 'style', 'tbody', 'figure', 'script'])
    },

    'ch_yes24_com': {  
        'date': ("span", {'class': "date"}),
        'title': ("p", {'class': "title"}),
        'text': ("div", {'class': ['txtBox', 'fr-view']}),
        'decompose': (['yb-root', 'blockquote', 'og-root', 'padding: 0px', 'articleTemp3', 'style', 'tbody', 'figure', 'script'])
    },

    'www_ddanzi_com': {  
        'date': ("p", {'class': "time"}),
        'title': ("h1", ),
        'text': ("div", {'class': 'read_content'}),
        'decompose': (['baseline;', 'tbody', 'img', 'script'])
    },

    'www_ikld_kr': {  
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': 'article-view-content-div'}),
        'decompose': (['editors', 'copyright', 'head-sub', 'tbody', 'figure', 'script'])
    },

    'news_ebs_co_kr': {  
        'date': ("p", {'class': "date"}),
        'title': ("h4", ),
        'text': ("div", {'class': 'view_con'}),
        'decompose': (['writer', 'copyright', 'like_area', 'tbody', 'figure', 'script'])
    },

    'www_mdilbo_com': {  
        'date': ("span", {'class': "txt_info"}),
        'title': ("h3", {'class': "tit_view"}),
        'text': ("div", {'class': 'article_view'}),
        'decompose': (['articleAD', 'style', 'tbody', 'figure', 'script'])
    },

    'www_youthdaily_co_kr': {  
        'date': ("ul", {'class': "art_info"}),
        'title': ("h2", ),
        'text': ("div", {'id': 'news_bodyArea'}),
        'decompose': (['imgframe', 'articleAD', 'style', 'tbody', 'figure', 'script'])
    },

    'www_redian_org': {  
        'date': ("div", {'class': "redian-view-date"}),
        'title': ("div", {'class': "redian-view-title"}),
        'text': ("div", {'class': 'pf-content'}),
        'decompose': (['style', 'tbody', 'figure', 'script'])
    },

    'www_mhns_co_kr': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': 'article-view-content-div'}),
        'decompose': (['relation', 'box-skin', 'tag-group', 'style', 'tbody', 'figure', 'script'])
    },

    'www_econovill_com': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': 'article-view-content-div'}),
        'decompose': (['tag-group', 'style', 'tbody', 'figure', 'script'])
    },

    'www_ebn_co_kr': {  
        'date': ("ul", {'id': "newsInfo"}),
        'title': ("h2", {'id': "newsTitle"}),
        'text': ("div", {'class': 'article'}),
        'decompose': (['text-align: center; font-size: 0.9em;', 'photo', 'subtitle', 'style', 'tbody', 'figure', 'script'])
    },

    'www_straightnews_co_kr': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': 'article-view-content-div'}),
        'decompose': (['subtitle', 'style', 'tbody', 'figure', 'script'])
    },

    'www_gndomin_com': {  
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': 'article-view-content-div'}),
        'decompose': (['editors', 'copyright', 'head-sub', 'style', 'tbody', 'figure', 'script'])
    },

    'www_ntoday_co_kr': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': 'article-view-content-div'}),
        'decompose': (['editors', 'copyright', 'head-sub', 'style', 'tbody', 'figure', 'script'])
    },

    'www_ikbc_co_kr': {  
        'date': ("div", {'class': "date"}),
        'title': ("h1", {'class': "title"}),
        'text': ("div", {'class': 'content'}),
        'decompose': (['copyright', 'head-sub', 'style', 'tbody', 'figure', 'script'])
    },

    'www_yonhapmidas_com': {  
        'date': ("div", {'class': "date"}),
        'title': ("h2", {'class': "article-title mtn ng-binding"}),
        'text': ("div", {'class': 'article-content'}),
        'decompose': (['copyright', 'head-sub', 'style', 'tbody', 'photo', 'script'])
    },

    'weekly_donga_com': {  
        'date': ("p", {'class': "info_time"}),
        'title': ("p", {'class': "title_text"}),
        'text': ("div", {'class': 'article_view'}),
        'decompose': (['copyright', 'head-sub', 'style', 'tbody', 'photo', 'script'])
    },

    'it_chosun_com': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': 'article-view-content-div'}),
        'decompose': (['copyright', 'head-sub', 'style', 'tbody', 'figure', 'script'])
    },

    'www_sejungilbo_com': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': 'article-view-content-div'}),
        'decompose': (['copyright', 'head-sub', 'style', 'tbody', 'figure', 'script'])
    },

    'www_thepublic_kr': {  
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': 'article-view-content-div'}),
        'decompose': (['tem-type-8', 'copy', 'head-sub', 'style', 'tbody', 'figure', 'script'])
    },

    'www_gnnews_co_kr': {  
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'class': 'news_text'}),
        'decompose': (['copy', 'head-sub', 'style', 'tbody', 'figure', 'script'])
    },


    'www_issuenbiz_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("div", {'class': "article-body"}),
        'decompose': (['writer','article-copy','figure', 'style', 'script','strong'])
    },

    'www_jeonmin_co_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("article", {'class': "article-veiw-body view-page font-size17"}),
        'decompose': (['view-copyright','view-editors','article-view-sns','float-left auto-padright-40','article-relation user-view default','figure', 'style', 'script','strong'])
    },

    'www_newsbrite_net': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("div", {'class': "article-body"}),
        'decompose': (['writer account','article-copy','like-group','figure', 'style', 'script'])
    },

    'news_inochong_org': {
        'date': ("div", {'style': "position:relative; padding-bottom:22px;border-bottom:1px solid #e6e6e6"}),
        'title': ("h2", {'class': "font_25 font_malgun"}),
        'text': ("div", {'id': "ct"}),
        'decompose': (['margin-top:30px','span','figure', 'style', 'script'])
    },

    'www_startuptoday_co_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['emoji-for','article-head-sub',"AD158760697626",'view-copyright','article-relation user-view custom box-skin design-13','view-editor','tag-group','figure', 'style', 'script'])
    },

    'www_jemin_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("div", {'class': "article-body"}),
        'decompose': (['subheading','writer','article-copy','figure', 'style', 'script'])
    },

    'www_paxnetnews_com': {
        'date': ("div", {'class': "nis-r-info-wrap"}),
        'title': ("div", {'class': "read-news-title"}),
        'text': ("div", {'class': "read-news-main-contents"}),
        'decompose': (['rnmc-left','rnmc-area','figure', 'style', 'script'])
    },

    'www_kpinews_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'class': "article-veiw-body view-page font-size17"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'www_newspost_kr': {
        'date': ("div", {'class': "info-group"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'www_newsjeju_net': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['tag-group','writer','article-copy','figure', 'style', 'script'])
    },

    'dealsite_co_kr': {
        'date': ("div", {'class': "nis-r-info-wrap"}),
        'title': ("div", {'class': "read-news-title"}),
        'text': ("div", {'class': "read-news-main-contents"}),
        'decompose': (['rnmc-area','rnmc-left','rnmc-relative-news','figure', 'style', 'script'])
    },

    'www_slist_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['article-footer','article-copy','figure', 'style', 'script'])
    },

    'tk_newdaily_co_kr': {
        'date': ("div", {'class': "article-date"}),
        'title': ("h1", {'class': ""}),
        'text': ("div", {'class': "article-body"}),
        'decompose': (['article-subtitle','center_img','figure', 'style', 'script'])
    },

    'www_betanews_net:8080': {
        'date': ("div", {'class': "date_ctrl_2011"}),
        'title': ("h2", {'class': "mt_art_tit"}),
        'text': ("div", {'id': "articleBody"}),
        'decompose': (['icaption','google-news-link','date_ctrl_2011','slink','hotnews','bot_ctrl_v4','art-wrap','article-sns2014','figure', 'style', 'script'])
    },

    'www_press9_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['article-head-sub','tag-group','view-copyright','view-editors','figure', 'style', 'script'])
    },

    'www_joygm_com': {
        'date': ("div", {'class': "view-info"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['article-copy','bot-sns','figure', 'style', 'script'])
    },

    'www_digitalbizon_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['article-copy','relation','writer','figure', 'style', 'script'])
    },

    'www_dongponews_net': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['view-copyright','color:#0000ff;','view-editors','figure', 'style', 'script'])
    },

    'www_vegannews_co_kr': {
        'date': ("ul", {'class': "art_info"}),
        'title': ("h2", {'class': ""}),
        'text': ("div", {'class': "cnt_view news_body_area"}),
        'decompose': (['figure', 'style', 'script','art_more'])
    },

    'www_newscape_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','AD165362489093'])
    },

    'www_newsmaker_or_kr': {
        'date': ("td", {'bgcolor': "EFEFEF"}),
        'title': ("td", {'class': "view_t"}),
        'text': ("td", {'class': "view_r"}),
        'decompose': (['font_imgdown_101302','figure', 'style', 'script'])
    },

    'www_gpkorea_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'class': "grid body"}),
        'decompose': (['writer','article-copy','figure', 'style', 'script'])
    },

    'cc_newdaily_co_kr': {
        'date': ("div", {'class': "article-date"}),
        'title': ("h1", {'class': ""}),
        'text': ("div", {'class': "news_zone"}),
        'decompose': (['noscript','guickguide','img-zoom','span','repoter-info display--flex--center pt20 pb0 mt30 bottom-repoter-profile','report-more display--flex--center widthfull font--size14 mb30','copyright','banner banner-side','editor-choice','banner','news_zone_02','figure', 'style', 'script'])
    },

    'www_mpmbc_co_kr': {
        'date': ("div", {'class': "col"}),
        'title': ("h1", {'class': "entry-title mt-1"}),
        'text': ("div", {'id': "journal_article_wrap"}),
        'decompose': (['mb-4 d-flex justify-content-between','author-box single-entry-section mt-4 mb-3','figure', 'style', 'script'])
    },

    'www_idsn_co_kr': {
        'date': ("dd", {'class': ""}),
        'title': ("h3", {'class': ""}),
        'text': ("div", {'id': "viewConts"}),
        'decompose': (['color:#494949; font-size:14px;','figure', 'style', 'script'])
    },

    'www_healthinnews_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'www_sctoday_co_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['article-head-sub','tag-group','emoji-for','view-copyright','view-editors','figure', 'style', 'script'])
    },

    'www_dailysecu_com': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['article-head-sub','articleview_jb','ad-template','view-copyright','view-editors','figure', 'style', 'script'])
    },

    'www_seoulwire_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['relation','tag-group','writer','article-copy','figure', 'style', 'script'])
    },

    'www_hellot_net': {
        'date': ("ul", {'class': "art_info"}),
        'title': ("h2", {'class': ""}),
        'text': ("div", {'id': "news_body_area"}),
        'decompose': (['imgframe','figure', 'style', 'script'])
    },

    'jmagazine_joins_com': {
        'date': ("div", {'class': "t-info"}),
        'title': ("h3", {'class': ""}),
        'text': ("div", {'class': "con_area"}),
        'decompose': (['color:#343F94;','nfortlbsize nfortbblL','table','figure', 'style', 'script'])
    },

    'dhnews_co_kr': {
        'date': ("dd", {'class': ""}),
        'title': ("h3", {'class': ""}),
        'text': ("div", {'class': "viewConts"}),
        'decompose': (['color:#494949; font-size:14px;','summary_title','_caption','figure', 'style', 'script'])
    },

    'www_traveltimes_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['account','article-copy','figure', 'style', 'script'])
    },

    'www_updownnews_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['writer','article-copy','figure', 'style', 'script'])
    },

    'edu_chosun_com': {
        'date': ("div", {'class': "article_etc"}),
        'title': ("div", {'class': "detail-subject"}),
        'text': ("div", {'class': "detail-content"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'www_taxwatch_co_kr': {
        'date': ("ul", {'class': "info"}),
        'title': ("h1", {'class': ""}),
        'text': ("div", {'class': "news_body new_editor"}),
        'decompose': (['atc','figure', 'style', 'script'])
    },

    'www_chemicalnews_co_kr': {
        'date': ("div", {'class': "info-group"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'www_ytnradio_kr': {
        'date': ("thead", {'class': ""}),
        'title': ("h2", {'class': ""}),
        'text': ("tbody", {'id': ""}),
        'decompose': (['figure', 'style', 'script'])
    },

    'www_constimes_co_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['article-head-sub','view-copyright','view-editors','figure', 'style', 'script'])
    },

    'www_pointdaily_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figcaption','writer','article-copy','figure', 'style', 'script'])
    },

    'enews_imbc_com': {
        'date': ("div", {'class': "ent-cont-ft"}),
        'title': ("h2", {'class': "title"}),
        'text': ("div", {'class': "ent-cont"}),
        'decompose': (['small','figure', 'style', 'script'])
    },

    'www_rwn_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['writer','article-copy','figure', 'style', 'script'])
    },

    'www_fsnews_co_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['article-head-sub','view-copyright','view-editors','figure', 'style', 'script'])
    },

    'weeklytrade_co_kr': {
        'date': ("dd", {'class': "info"}),
        'title': ("dt", {'class': "title"}),
        'text': ("div", {'id': "article_text"}),
        'decompose': (['news_caption','figure', 'style', 'script'])
    },

    'www_kmedinfo_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['writer','article-copy','figure', 'style', 'script'])
    },

    'news_ifm_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figcaption','writer','article-copy','figure', 'style', 'script'])
    },

    'www_medigatenews_com': {
        'date': ("p", {'class': "update"}),
        'title': ("p", {'class': "titxt"}),
        'text': ("div", {'class': "content_print"}),
        'decompose': (['subtxt','image','doc_notice','copyright','taglist','util','figure', 'style', 'script'])
    },

    'www_monews_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['emoji-for','relation','tag-group','writer','article-copy','figure', 'style', 'script'])
    },

    'www_foodnews_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['color:#2980b9;','size-17','article-view-sns','writer','article-copy','figure', 'style', 'script'])
    },

    'www_agrinet_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['strong','figure', 'style', 'script'])
    },

    'jejumbc_com': {
        'date': ("div", {'class': "col"}),
        'title': ("h1", {'class': "entry-title mt-1"}),
        'text': ("div", {'id': "journal_article_wrap"}),
        'decompose': (['author-box single-entry-section mt-4 mb-3','figure', 'style', 'script'])
    },

    'www_electimes_com': {
        'date': ("ul", {'class': "info no-bullet text-right"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['subheading','tag-group','relation','account','article-copy','figure', 'style', 'script'])
    },

    'enter_etoday_co_kr': {
        'date': ("div", {'class': "byline"}),
        'title': ("h2", {'class': ""}),
        'text': ("div", {'class': "biz_view_cont"}),
        'decompose': (['img_box_desc','reporter','reporter_copy_w','figure', 'style', 'script'])
    },

    'www_eroun_net': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['writer account','article-copy','like-group','figure', 'style', 'script'])
    },

    'cnbc_sbs_co_kr': {
        'date': ("div", {'class': "ah_info"}),
        'title': ("h3", {'class': "ah_big_title"}),
        'text': ("div", {'class': "ab_text fsize4"}),
        'decompose': (['strong','article-copy','like-group','figure', 'style', 'script'])
    },

    'www_s-journal_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['article-copy','figure', 'style', 'script'])
    },

    'www_cmbkj_co_kr': {
        'date': ("div", {'class': "ABA-info-box", 'style': 'color:#777;'}),
        'title': ("h1", {'style': "font-size: 14px !important;"}),
        'text': ("div", {'class': "ABA-view-body ABA-article-contents"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'www_smartfn_co_kr': {
        'date': ("div", {'class': "info"}),
        'title': ("h1", {'class': "title"}),
        'text': ("div", {'id': "body_wrap"}),
        'decompose': (['copyright','figure', 'style', 'script'])
    },

    'www_tournews21_com': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['article-head-sub','view-copyright','view-editors','bottom-box','figure', 'style', 'script'])
    },

    'www_job-post_co_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['view-copyright','view-editors','bottom-box','figure', 'style', 'script'])
    },

    'www_opinionnews_co_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['article-head-sub','background: rgb(238, 238, 238); padding: 5px 10px; border: 1px solid rgb(204, 204, 204); border-image: none;','background:#eeeeee;border:1px solid #cccccc;padding:5px 10px;','view-copyright','view-editors','bottom-box','figure', 'style', 'script'])
    },

    'www_safetynews_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("div", {'class': "article-body"}),
        'decompose': (['subheading','tag-group','writer','article-copy','figure', 'style', 'script'])
    },

    'www_withinnews_co_kr': {
        'date': ("dd", {'class': "info"}),
        'title': ("dt", {'class': "title"}),
        'text': ("div", {'id': "article_text"}),
        'decompose': (['font','figure', 'style', 'script'])
    },

    'www_it-b_co_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['article-head-sub','view-copyright','view-editors','figure', 'style', 'script'])
    },

    'www_knpnews_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['article-view-sns','writer','article-copy','figure', 'style', 'script'])
    },

    'www_munhaknews_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'www_nbnews_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['tag-group','writer','figure', 'style', 'script'])
    },

    'kizmom_hankyung_com': {
        'date': ("div", {'class': "top_con"}),
        'title': ("p", {'class': "tit zoominout"}),
        'text': ("div", {'class': "newscon mt39 zoominout"}),
        'decompose': (['newsinfo mt39','view_bt_ad','v_topimg_wrap','_popIn_recommend','figure', 'style', 'script'])
    },

    'www_hapt_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['writer','article-copy','figure', 'style', 'script'])
    },

    'www_newswell_co_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['article-head-sub','tag-group','view-copyright','view-editors','figure', 'style', 'script'])
    },

    'www_kfenews_co_kr': {
        'date': ("ul", {'class': "infos"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['article-sns','article-copy','figure', 'style', 'script'])
    },

    'www_ccreview_co_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "articleBody"}),
        'decompose': (['view-copyright','view-editors','figure', 'style', 'script'])
    },

    'www_hellodd_com': {
        'date': ("div", {'class': "info-group"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['article-sns','article-copy','writer','figure', 'style', 'script'])
    },

    'www_ktsketch_co_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['view-copyright','view-editors','tag-group','tem-type-8','figure', 'style', 'script'])
    },

    'www_m-economynews_com': {
        'date': ("ul", {'class': "art_info"}),
        'title': ("h2", {'class': ""}),
        'text': ("div", {'class': "cnt_view news_body_area"}),
        'decompose': (['strong','art_more','figure', 'style', 'script'])
    },

    'www_sisajournal-e_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['article-copy','tag-group','writer','social-group','figure', 'style', 'script'])
    },

    'www_edupress_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['view-copyright','view-editors','figure', 'style', 'script'])
    },

    'news_wowtv_co_kr': {
        'date': ("p", {'class': "date-news"}),
        'title': ("h1", {'class': "title-news"}),
        'text': ("div", {'class': "box-news-body"}),
        'decompose': (['ADinContents','photoBanner','figure', 'style', 'script'])
    },

    'byline_network': {
        'date': ("span", {'class': "posted-on"}),
        'title': ("h1", {'class': "entry-title"}),
        'text': ("div", {'class': "entry-content single-content"}),
        'decompose': (['wp-block', 'entry-footer', 'figure', 'script'])
    },

    'www_venturesquare_net': {
        'date': ("div", {'class': "entry-meta"}),
        'title': ("h1", {'class': "h2 entry-title primary-500 bold"}),
        'text': ("div", {'class': "entry-content bt-gray-200 pt-5"}),
        'decompose': (['strong','share','sharedaddy sd-block sd-like jetpack-likes-widget-wrapper jetpack-likes-widget-loaded','oembed','sharedaddy sd-block sd-like jetpack-likes-widget-wrapper jetpack-likes-widget-loaded','jp-relatedposts','sharedaddy sd-sharing-enabled','figure', 'style', 'script'])
    },

    'www_lcnews_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['article-copy','social-group','writer','figure', 'style', 'script'])
    },

    'www_bizwatch_co_kr': {
        'date': ("ul", {'class': "info"}),
        'title': ("h1", {'class': ""}),
        'text': ("div", {'itemprop': "articleBody"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'www_usmbc_co_kr': {
        'date': ("div", {'class': "col"}),
        'title': ("h1", {'class': "entry-title mt-1"}),
        'text': ("div", {'id': "journal_article_wrap"}),
        'decompose': (['figure', 'style', 'script'])
    },


    'www_itnews_or_kr': {
        'date': ("div", {'class': "td-module-meta-info"}),
        'title': ("h1", {'class': "entry-title"}),
        'text': ("div", {'id': "journal_article_wrap"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'fpn119_co_kr': {
        'date': ("div", {'class': "read_option_top"}),
        'title': ("h1", {'class': "read_title"}),
        'text': ("div", {'id': "textinput"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'www_inven_co_kr': {
        'date': ("dl", {'class': "date"}),
        'title': ("div", {'class': "title"}),
        'text': ("div", {'id': "imageCollectDiv"}),
        'decompose': (['figure', 'copy', 'script'])
    },

    'www_energy-news_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'www_mstoday_co_kr': {
        'date': ("div", {'class': "info-group"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'lady_khan_co_kr': {
        'date': ("div", {'class': "byline"}),
        'title': ("h1", {'class': "article_head"}),
        'text': ("div", {'class': "art_body font_opt3"}),
        'decompose': (['caption','editor-openlink-horizontal','figure', 'style', 'script'])
    },

    'www_housingherald_co_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['strong','view-copyright','view-editors','figure', 'style', 'script'])
    },

    'tvdaily_co_kr': {
        'date': ("font", {'class': "read_time"}),
        'title': ("font", {'class': "read_title"}),
        'text': ("div", {'class': "read"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'www_newsverse_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'woman_donga_com': {
        'date': ("div", {'class': "name_date"}),
        'title': ("h2", {'class': ""}),
        'text': ("div", {'class': "article_box"}),
        'decompose': (['photo_center','sub','figure', 'style', 'script'])
    },

    'www_biztribune_co_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['view-copyright','view-editors','figure', 'style', 'script'])
    },

    'jtbcgolf_joins_com': {
        'date': ("p", {'class': "news_s_v_title_s"}),
        'title': ("p", {'class': "news_s_v_title"}),
        'text': ("div", {'id': "newscontent"}),
        'decompose': (['reporter','figure', 'style', 'script'])
    },

    'www_koreaittimes_com': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['view-copyright','view-editors','photo-layout','figure', 'style', 'script'])
    },

    'kids_donga_com': {
        'date': ("ul", {'class': ""}),
        'title': ("li", {'class': "title"}),
        'text': ("div", {'class': "at_content"}),
        'decompose': (['color:rgb(255, 108, 0)','font-family: 돋움,dotum; font-size: 10pt;','figure', 'style', 'script'])
    },

    'www_sisacast_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['article-head-sub','tag-group','view-copyright','view-editors','figure', 'style', 'script'])
    },
    
    'www_niceeconomy_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['article-head-sub','tag-group','view-copyright','view-editors','figure', 'style', 'script'])
    },

    'theviewers_co_kr': {
        'date': ("div", {'class': "info-area"}),
        'title': ("h4", {'class': "tit-big"}),
        'text': ("div", {'class': "cont-area"}),
        'decompose': (['updown_area print-none','sns-area-bottom print-none','shadow-box','figure', 'style', 'script'])
    },

    'www_esgeconomy_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['updown_area print-none','sns-area-bottom print-none','shadow-box','figure', 'style', 'script'])
    },

    'www_gosiweek_com': {
        'date': ("dd", {'class': ""}),
        'title': ("h3", {'class': ""}),
        'text': ("div", {'class': "viewConts"}),
        'decompose': (['font-size: 24pt;','color:#494949; font-size:14px;','figure', 'style', 'script'])
    },

    'www_epnc_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['copy-txt-box','figure', 'style', 'script'])
    },

    'www_mediawatch_kr': {
        'date': ("ul", {'class': "art_info"}),
        'title': ("h2", {'class': ""}),
        'text': ("div", {'class': "cnt_view news_body_area"}),
        'decompose': (['letter-spacing: -0.9px; text-align: left; line-height: 1.76 !important;','art_more','color: rgb(0, 0, 255);','figure', 'style', 'script'])
    },

    'www_factin_co_kr': {
        'date': ("div", {'class': "info"}),
        'title': ("h1", {'class': "title"}),
        'text': ("div", {'class': "content"}),
        'decompose': (['copyright','figure', 'style', 'script'])
    },


    'www_joynews24_com': {
        'date': ("nav", {'class': "view"}),
        'title': ("h1", {'class': ""}),
        'text': ("article", {'class': "view font16"}),
        'decompose': (['blank','address','author-list','figure', 'style', 'script'])
    },

    'bravo_etoday_co_kr': {
        'date': ("div", {'class': "newsinfo"}),
        'title': ("h1", {'class': "main_title"}),
        'text': ("div", {'class': "articleView"}),
        'decompose': (['newsdata','block_box','byline','recommend_btn','kwd_tags','img_box_desc','figure', 'style', 'script'])
    },

    'www_newsian_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['newsdata','block_box','byline','recommend_btn','kwd_tags','img_box_desc','figure', 'style', 'script'])
    },

    'www_tokenpost_kr': {
        'date': ("div", {'class': "view_day"}),
        'title': ("h1", {'class': "view_top_title noselect"}),
        'text': ("div", {'class': "article_content"}),
        'decompose': (['newsdata','block_box','byline','recommend_btn','kwd_tags','img_box_desc','figure', 'style', 'script'])
    },

    'www_newscammp_co_kr': {
        'date': ("div", {'class': "info"}),
        'title': ("h1", {'class': "title"}),
        'text': ("div", {'class': "content"}),
        'decompose': (['copyright','figure', 'style', 'script'])
    },

    'www_lec_co_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['view-copyright','view-editors','figure', 'style', 'script'])
    },

    'www_ize_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['view-copyright','view-editors','figure', 'style', 'script'])
    },

    'ccn_hcn_co_kr': {
        'date': ("div", {'class': "date"}),
        'title': ("h2", {'class': ""}),
        'text': ("div", {'class': "memo"}),
        'decompose': (['sns_g','figure', 'style', 'script'])
    },

    'www_the-pr_co_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['article-head-sub','tem-type-8','tag-group','view-copyright','view-editors','figure', 'style', 'script'])
    },

    'news_kotra_or_kr': {
        'date': ("div", {'class': "txtInfo"}),
        'title': ("div", {'class': "txtL"}),
        'text': ("div", {'class': "view_txt"}),
        'decompose': (['add_openNoti','txt_copyRightHolder','line-height: 107%;','figure', 'style', 'script'])
    },

    'www_dandinews_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'www_newswatch_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['strong','writer','article-copy','figure', 'style', 'script'])
    },

    'www_thefirstmedia_net': {
        'date': ("div", {'class': "curation-view-dated"}),
        'title': ("div", {'class': "title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figcaption','bot-sns','view-copyright','article-control','editor-profile', 'figure','style', 'script'])
    },

    'www_interview365_com': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['article-head-sub','tag-group','view-copyright','view-editors','figcaption', 'figure','style', 'script'])
    },

    'www_interfootball_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['article-head-sub','tag-group','view-copyright','view-editors','figcaption','figure', 'style', 'script'])
    },

    'www_ggmedinews_com': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['article-head-sub','tag-group','view-copyright','view-editors','figcaption','article-relation user-view default', 'figure','style', 'script'])
    },

    'www_travie_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['tag-group','writer','article-copy','figure', 'style', 'script'])
    },

    'www_fashionn_com': {
        'date': ("tbody", {'class': ""}),
        'title': ("h3", {'class': "title"}),
        'text': ("div", {'class': "view_body"}),
        'decompose': (['view_copyright','figure', 'style', 'script'])
    },

    'www_thedrive_co_kr': {
        'date': ("dd", {'class': ""}),
        'title': ("h3", {'class': ""}),
        'text': ("div", {'class': "viewConts"}),
        'decompose': (['_caption','color:#494949; font-size:14px;','figure', 'style', 'script'])
    },

    'www_tbc_co_kr': {
        'date': ("div", {'id': "article-view"}),
        'title': ("div", {'class': "col-9"}),
        'text': ("p", {'id': "article_body"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'www_newsculture_press': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['tag-group','byeline','writer','anchorBtm','figure', 'style', 'script'])
    },

    'sports_mk_co_kr': {
        'date': ("td", {'style': "padding:15px 0 0 20px;"}),
        'title': ("span", {'class': "head_tit"}),
        'text': ("div", {'class': "read_txt"}),
        'decompose': (['tag-group','byeline','writer','anchorBtm','figure', 'style', 'script'])
    },

    'www_nbntv_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['writer','anchorBtm','figure', 'style', 'script'])
    },

    'www_hg-times_com': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "articleBody"}),
        'decompose': (['tag-group','article-body-dn-txt auto-marbtm-50 no-bullet','editor-profile','emoji-for','emoji-tit','hw-box','view-copyright','figure', 'style', 'script'])
    },

    'sateconomy_co_kr': {
        'date': ("dd", {'class': ""}),
        'title': ("h3", {'class': ""}),
        'text': ("div", {'class': "viewConts"}),
        'decompose': (['color:#494949; font-size:14px;','summary_title','_caption','figure', 'style', 'script'])
    },

    'jtv_co_kr': {
        'date': ("div", {'class': "info"}),
        'title': ("h1", {'class': "fs25"}),
        'text': ("div", {'id': "vContent"}),
        'decompose': (['color:#494949; font-size:14px;','summary_title','_caption','figure', 'style', 'script'])
    },

    'www_dailyvet_co_kr': {
        'date': ("div", {'class': "column is-6 left"}),
        'title': ("h1", {'class': "page-title"}),
        'text': ("div", {'class': "pf-content"}),
        'decompose': (['columns is-gapless bottom-author-wrapper is-mobile','bottom-like-wrapper','article-tags-wrapper','related-posts-wrapper','comment','article-bottom-ads','figure', 'style', 'script'])
    },

    'www_greenpostkorea_co_kr': {
        'date': ("div", {'class': "info-group"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['tag-group','writer','article-copy','figure', 'style', 'script'])
    },

    'gj_newdaily_co_kr': {
        'date': ("div", {'class': "article-date"}),
        'title': ("h1", {'class': ""}),
        'text': ("div", {'class': "article-body"}),
        'decompose': (['article-subtitle','img-caption','figure', 'style', 'script'])
    },

    'www_ulsanpress_net': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['writer','article-copy','account','name','figure', 'style', 'script'])
    },
     
    'platum_kr': {
        'date': ("div", {'class': "post_detail post_date"}),
        'title': ("h1", {'class': ""}),
        'text': ("div", {'class': "post_header single"}),
        'decompose': (['wp_rp_wrap  wp_rp_plain','wp_rp_content','post_share_center','post_excerpt post_tag','figure', 'style', 'script'])
    },

    'www_tleaves_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['writer','article-copy','figure', 'style', 'script'])
    },

    'www_medisobizanews_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['writer','article-copy','figure', 'style', 'script'])
    },

    'www_suwonilbo_kr': {
        'date': ("div", {'class': "info-box"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['tag-group','writer','article-copy','figure', 'style', 'script'])
    },

    'www_insightkorea_co_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'class': "cont-body"}),
        'decompose': (['tag-group','view-copyright','view-editors','figure', 'style', 'script'])
    },

    'stoo_com': {
        'date': ("div", {'class': "area_data"}),
        'title': ("h4", {'class': ""}),
        'text': ("div", {'id': "article"}),
        'decompose': (['byeline','td','figure', 'style', 'script'])
    },

    'www_movist_com': {
        'date': ("div", {'class': "conNewsTitle"}),
        'title': ("span", {'class': "titC"}),
        'text': ("div", {'class': "conNewsBody"}),
        'decompose': (['byeline','td','figure', 'style', 'script'])
    },

    'www_travelitoday_com': {
        'date': ("div", {'class': "publication"}),
        'title': ("h4", {'class': ""}),
        'text': ("div", {'class': "newTemp newType1"}),
        'decompose': (['subExp','figure', 'style', 'script'])
    },

    'www_mediafine_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['writer','comment','grid side','article-copy','figure', 'style', 'script'])
    },

    'www_chungnamilbo_com': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['view-copyright','view-editors','figure', 'style', 'script'])
    },

    'view_heraldcorp_com': {
        'date': ("div", {'class': "article_top"}),
        'title': ("li", {'class': "article_title ellipsis2"}),
        'text': ("div", {'id': "articleText"}),
        'decompose': (['view-copyright','view-editors','figure', 'style', 'script'])
    },


    'www_iusm_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("div", {'class': "article-body"}),
        'decompose': (['figure', 'style', 'script','article-footer','article-copy'])
    },    

    'www_mkhealth_co_kr': {
        'date': ("div", {'class': "info-group"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("div", {'class': "article-body"}),
        'decompose': (['figure', 'style', 'script','subheading','relation', 'tag-group', 'writer','article-copy'])
    },    

    'www_kyosu_net': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','article-head-sub','strong', 'tag-group', 'view-editors','view-copyright'])
    },    

    'www_100ssd_co_kr': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','strong', 'banner_box', 'view-editors','view-copyright'])
    },   
    
    'www_chungnamilbo_co_kr': {
        'date': ("ul", {'class': "infos"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script'])
    }, 

    'www_psnews_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script'])
    },   

    'www_whosaeng_com': {
        'date': ("div", {'class': "writer_time"}),
        'title': ("h1", {'class': "read_title"}),
        'text': ("div", {'id': "textinput"}),
        'decompose': (['figure', 'style', 'script'])
    },   

    'www_ltn_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script', 'group', 'relation', 'writer', 'copy'])
    },   

    'economychosun_com': {
        'date': ("div", {'class': "bookNo-date"}),
        'title': ("h1", {'class': "article--main-title"}),
        'text': ("div", {'class': "conts article--contents-area box--margin-center"}),
        'decompose': (['figure', 'style', 'script', 'date_text'])
    },   

    'www_jeollailbo_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script'])
    },   

    'www_newmanagement_co_kr': {
        'date': ("div", {'class': "SingleDate"}),
        'title': ("h1", ),
        'text': ("div", {'class': "TextBox"}),
        'decompose': (['figure', 'style', 'script'])
    },   

    'www_ikpnews_net': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script'])
    },   

    'idsn_co_kr': {
        'date': ("div", {'class': "viewTitle"}),
        'title': ("h3", ),
        'text': ("div", {'class': "viewConts"}),
        'decompose': (['figure', 'style', 'script','se_tbl'])
    },   

    'dream_kotra_or_kr': {
        'date': ("li", {'class': "date"}),
        'title': ("div", {'class': "txtL"}),
        'text': ("div", {'class': "view_txt"}),
        'decompose': (['figure', 'style', 'script','copyRight'])
    },   

    'www_ddaily_co_kr': {
        'date': ("div", {'class': "byline"}),
        'title': ("p", {'class': "title"}),
        'text': ("div", {'class': "article_content"}),
        'decompose': (['figure', 'style', 'script'])
    },   

    'www_tfmedia_co_kr': {
        'date': ("ul", {'class': "art_info"}),
        'title': ("h2", ),
        'text': ("div", {'class': "cnt_view news_body_area"}),
        'decompose': (['figure', 'style', 'script','art_more'])
    },   

    'www_nbntv_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script'])
    },   

    'www_incheonin_com': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script', 'copyright', 'editors','head-sub'])
    },   

    'www_starnewskorea_com': {
        'date': ("span", {'class': "write mgt11"}),
        'title': ("h1", {'class': "at_tit2"}),
        'text': ("div", {'id': "textBody"}),
        'decompose': (['figure', 'style', 'script', 'desc'])
    },   

    'www_cjb_co_kr': {
        'date': ("dl", {'class': "info"}),
        'title': ("h1", {'class': "view-title"}),
        'text': ("div", {'class': "view-content"}),
        'decompose': (['figure', 'style', 'script'])
    },   

    'www_siminsori_com': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','copyright','editors'])
    },   

    'www_cts_tv': {
        'date': ("ul", {'class': "info"}),
        'title': ("h1", {'class': "title"}),
        'text': ("div", {'class': "body textarea"} ),
        'decompose': (['figure', 'style', 'script','head-sub','copyright','editors'])
    },   

    'www_topdaily_kr': {
        'date': ("span", {'class': "published_at"}),
        'title': ("h1", ),
        'text': ("section", {'class': "article-body"} ),
        'decompose': (['figure', 'style', 'script','hashtags','subtitle','byline','stock-news', 'main-news', 'related-news','copyright','editors'])
    },   

    'www_cstimes_com': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','tag-group','copyright','editors'])
    },   

    'www_srtimes_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','tag-group','copyright','editors'])
    },   

    'www_fortunekorea_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','tag-group','copyright','editors'])
    },   

    'www_newsmin_co_kr': {
        'date': ("div", {'class': "td-module-meta-info"}),
        'title': ("h1", {'class': "entry-title"}),
        'text': ("div", {'class': "td-post-content"}),
        'decompose': (['figure', 'style', 'script','audio-table', 'sns','quote_box','editors'])
    },   

    'www_megaeconomy_co_kr': {
        'date': ("div", {'class': "viewTitle"}),
        'title': ("h3", ),
        'text': ("div", {'class': "viewConts"}),
        'decompose': (['figure', 'style', 'script','summary_title', 'banner','quote_box','editors'])
    },   

    'www_pinpointnews_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3",{'class': "heading"} ),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','summary_title', 'banner','quote_box','editors'])
    },   

    'www_journalist_or_kr': {
        'date': ("div", {'class': "byline"}),
        'title': ("p",{'class': "title"} ),
        'text': ("div", {'id': "news_body_area"}),
        'decompose': (['figure', 'style', 'script','all_article_list', 'banner','quote_box','editors'])
    },   

    'www_kwangju_co_kr': {
        'date': ("div", {'class': "Tline"}),
        'title': ("div",{'class': "rtitle1"} ),
        'text': ("div", {'id': "joinskmbox"}),
        'decompose': (['figure', 'style', 'script','all_article_list', 'banner','quote_box','editors'])
    },   

    'www_news2day_co_kr': {
        'date': ("div", {'class': "date"}),
        'title': ("h2",{'class': "subject"} ),
        'text': ("div", {'class': "view_con cf"}),
        'decompose': (['figure', 'style', 'script','img-caption', 'banner','quote_box','editors'])
    },   

    'www_djtimes_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3",{'class': "heading"} ),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','all_article_list', 'banner','quote_box','editors'])
    },   

    'www_impacton_net': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1",{'class': "heading"} ),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','tem-type-2', 'banner','quote_box','editors'])
    },   

    'www_dkilbo_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3",{'class': "heading"} ),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','tem-type-2', 'banner','quote_box','editors'])
    },   

    'news_bizwatch_co_kr': {
        'date': ("ul", {'class': "info"}),
        'title': ("h1", ),
        'text': ("div", {'itemprop': "articleBody"}),
        'decompose': (['figure', 'style', 'script','tem-type-2', 'banner','quote_box','editors'])
    },   

    'www_ftoday_co_kr': {
        'date': ("div", {'class': "info-group"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','tem-type-2', 'banner','quote_box','editors'])
    },   

    'www_newsgn_com': {
        'date': ("div", {'class': "info-group"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','tem-type-2', 'banner','quote_box','editors'])
    },   

    'www_jejuilbo_net': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'class': "cont-body"}),
        'decompose': (['figure', 'style', 'script','tem-type-2', 'banner','quote_box','editors'])
    },   

    'www_lawleader_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','tem-type-2', 'banner','quote_box','editors'])
    },   

    'isplus_com': {
        'date': ("div", {'class': "journalist_date text_15 color_999"}),
        'title': ("p", {'class': "sub_tit"}),
        'text': ("div", {'class': "view_txt pl_10 article_body"}),
        'decompose': (['figure', 'style', 'script','tem-type-2', 'banner','quote_box','editors'])
    },   

    'www_apnews_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','tem-type-2', 'banner','quote_box','editors'])
    },   

    'www_energydaily_co_kr': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','copyright','editors'])
    },  

    'www_kdpress_co_kr': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','copyright','editors'])
    },  

    'www_efnews_co_kr': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','tag-group','copyright','editors'])
    },  

    'www_meconomynews_com': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','writer', 'tag-group','copyright','editors'])
    },  

    'ch1_skbroadband_com': {
        'date': ("span", {'class': "date"}),
        'title': ("h4", {'class': "h4_title"}),
        'text': ("div", {'class': "content_s"}),
        'decompose': (['figure', 'style', 'script','head-sub','writer', 'tag-group','copyright','editors'])
    },  

    'www_jmbc_co_kr': {
        'date': ("span", {'class': "broad_date"}),
        'title': ("span", {'class': "subject"}),
        'text': ("div", {'class': "contents_wrap news"}),
        'decompose': (['figure', 'style', 'script','head-sub','writer', 'tag-group','copyright','editors'])
    },  

    'www_doctorstimes_com': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','emoji', 'writer', 'tag-group','copyright','editors'])
    },  

    'www_onews_tv': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','emoji', 'writer', 'tag-group','copyright','editors'])
    },  

    'www_ujeil_com': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-info"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','emoji', 'writer', 'tag-group','copyright','editors'])
    },  

    'www_kbmaeil_com': {
        'date': ("div", {'class': "info-group"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','emoji','copyright','editors'])
    },  

    'www_ziksir_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','emoji','copyright','editors'])
    },      

    'www_ablenews_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','emoji','copyright','editors'])
    },     

    'www_lkp_news': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','emoji','copyright','editors'])
    },     

    'dgmbc_com': {
        'date': ("div", {'class': "col"}),
        'title': ("h1", {'class': "entry-title mt-1"}),
        'text': ("div", {'id': "journal_article_wrap"}),
        'decompose': (['figure', 'style', 'script','head-sub','emoji','copyright','editors'])
    },   

    'worknworld_kctu_org': {
        'date': ("div", {'class': "article-info"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','emoji','copyright','editors'])
    },       

    'www_rapportian_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','emoji','copyright','editors'])
    }, 

    'www_k-health_com': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','tag-group','copyright','editors'])
    }, 

    'jhealthmedia_joins_com': {
        'date': ("div", {'class': "byline"}),
        'title': ("h1", {'class': "headline nsk"}),
        'text': ("div", {'id': "articleBody"}),
        'decompose': (['figure', 'style', 'script','head-sub','tag-group','copyright','editors'])
    }, 

    'www_civicnews_com': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','tag-group','copyright','editors'])
    }, 

    'www_banronbodo_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','tag-group','copyright','editors'])
    }, 

    'gg_newdaily_co_kr': {
        'date': ("div", {'class': "article-date"}),
        'title': ("h1", ),
        'text': ("li", {'class': "par"}),
        'decompose': (['figure', 'style', 'script','head-sub','tag-group', 'img-zoom', 'copyright','editors'])
    }, 

    'www_junggi_co_kr': {
        'date': ("dd", {'class': "writer_info"}),
        'title': ("h3", ),
        'text': ("dd", {'class': "news_content fontSizeChangeLayer"}),
        'decompose': (['figure', 'style', 'script','head-sub','view_copy', 'ul', 'copyright','editors'])
    }, 

    'www_newskr_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','tag-group','copyright','editors'])
    }, 

    'www_koreahealthlog_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','8f1i','copyright','editors'])
    }, 

    'www_fetv_co_kr': {
        'date': ("ul", {'class': "art_info"}),
        'title': ("h2", ),
        'text': ("div", {'class': "cnt_view news_body_area"}),
        'decompose': (['figure', 'style', 'script','head-sub','art_more','copyright','editors'])
    }, 

    'www_ezyeconomy_com': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','tag-group','copyright','editors'])
    }, 

    'www_thebell_co_kr': {
        'date': ("div", {'class': "userBox"}),
        'title': ("p", {'class': "tit"}),
        'text': ("div", {'class': "viewSection"}),
        'decompose': (['figure', 'style', 'script','editBox','tit_np','tip','banner'])
    }, 

    'www_newsfc_co_kr': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','tag-group','copyright','editors'])
    }, 

    'www_worktoday_co_kr': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','tag-group','copyright','editors'])
    }, 

    'www_wolyo_co_kr': {
        'date': ("div", {'class': "info-group"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','tag-group','copyright','editors'])
    }, 

    'www_kbiznews_co_kr': {
        'date': ("div", {'class': "info-group"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','tag-group','copyright','editors'])
    }, 

    'www_ibabynews_com': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','tag-group','banner', 'columns','copyright','editors'])
    }, 

   'www_idjnews_kr': {
        'date': ("div", {'class': "info-group"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','tag-group','banner', 'copyright','editors'])
    }, 

   'www_newsquest_co_kr': {
        'date': ("div", {'class': "info-group"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','tag-group','banner', 'copyright','editors'])
    }, 

   'www_babytimes_co_kr': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','tag-group','banner', 'copyright','editors'])
    }, 

   'www_pharmnews_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','subtitle','tag-group','byline', 'copyright','editors'])
    }, 

   'www_e2news_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','subtitle','tag-group','byline', 'copyright','editors'])
    }, 

   'www_kbanker_co_kr': {
        'date': ("div", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','subtitle','tag-group','byline', 'copyright','editors'])
    }, 

   'www_jejumaeil_net': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','subtitle','tag-group','byline', 'copyright','editors'])
    }, 

   'www_discoverynews_kr': {
        'date': ("div", {'class': "info-group"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','subtitle','tag-group','byline', 'copyright','editors'])
    }, 

   'www_wikileaks-kr_org': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','banner','sns', 'toolkit', 'reply', 'replay', 'copyright','editors'])
    }, 

   'www_sisapress_com': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','banner','sns', 'toolkit', 'reply', 'replay', 'copyright','editors'])
    }, 

   'www_intn_co_kr': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','banner','sns', 'clearfix', 'reply', 'replay', 'copyright','editors'])
    }, 

   'digitalchosun_dizzo_com': {
        'date': ("div", {'class': "headline"}),
        'title': ("h3", {'class': "subject"}),
        'text': ("div", {'id': "article"}),
        'decompose': (['figure', 'style', 'script','img','sub_tit','linkers','reporter', 'clearfix', 'reply', 'replay', 'copyright','editors'])
    }, 

   'www_queen_co_kr': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','banner','sns', 'copyright','editors'])
    }, 

    'www_thereport_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub'])
    }, 

    'www_bloter_net': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub'])
    }, 

    'cwn_kr': {
        'date': ("div", {'class': "viewTitle"}),
        'title': ("h3", ),
        'text': ("div", {'itemprop': "articleBody"}),
        'decompose': (['figure', 'style', 'script','summary', 'tag', 'caption'])
    }, 

    'www_datasom_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub'])
    }, 

    'www_mhj21_com': {
        'date': ("div", {'class': "writer_time"}),
        'title': ("h1", {'class': "read_title"}),
        'text': ("div", {'id': "textinput"}),
        'decompose': (['figure', 'style', 'script','caption','bold'])
    }, 

    'thepublic_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','copy'])
    }, 

    'www_cctvnews_co_kr': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','copy','tag','editor'])
    }, 

    'www_cctimes_kr': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','head-sub','copy','tag','editor'])
    }, 

    'www_incheonnews_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script'])
    }, 

    'www_artinsight_co_kr': {
        'date': ("div", {'class': "view01_date"}),
        'title': ("div", {'class': "news_title01"} ),
        'text': ("div", {'id': "view_content"}),
        'decompose': (['figure', 'style', 'script'])
    }, 

    'www_konas_net': {
        'date': ("span", {'class': "date"}),
        'title': ("p", {'class': "NEWS-view-title"} ),
        'text': ("div", {'class': "cont"}),
        'decompose': (['figure', 'style', 'script'])
    }, 

    'www_catholicpress_kr': {
        'date': ("div", {'class': "article-head-info"}),
        'title': ("div", {'class': "article-head-title"} ),
        'text': ("div", {'class': "fr-view"}),
        'decompose': (['figure', 'style', 'script','caption','quote'])
    }, 


    'www_bizhankook_com': {
        'date': ("span", {'class': "date"}),
        'title': ("h2", {'class': "tit"}),
        'text': ("section", {'class': "viewContWrap"}),
        'decompose': (['figure', 'style', 'script','relation','copy','btn','h3','journalist','another'])
    }, 

    'www_newsclaim_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','relation','naver'])
    }, 

    'www_smedaily_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','relation'])
    }, 

    'www_dailypop_kr': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','editor','copy'])
    },

    'www_ikunkang_com': {
        'date': ("li", {'class': "date"}),
        'title': ("font", {'class': "headline-title"}),
        'text': ("div", {'class': "cont-body"}),
        'decompose': (['figure', 'style', 'script','caption','keywordView','martop','editor','copy'])
    }, 

    'busanmbc_co_kr': {
        'date': ("span", {'class': "purple_5"}),
        'title': ("p", {'class': "txt_left font_h1 white mg_0 mt_10 mb_10 font_bold"}),
        'text': ("div", {'class': "newsvbox_tp2 single-body entry-content typography-copy mt_20"}),
        'decompose': (['figure', 'style', 'script','relation'])
    }, 

    'www_autodaily_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','editor','copy'])
    },

    'journal_kobeta_com': {
        'date': ("div", {'class': "meta-info"}),
        'title': ("h1", {'class': "entry-title"}),
        'text': ("div", {'class': "td-post-content td-pb-padding-side"}),
        'decompose': (['figure', 'style', 'script','editor','copy','sns'])
    },

    'www_goodkyung_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','editor','copy'])
    },

    'www_todaykorea_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','editor','subtitle','img','copy','banner'])
    },

    'www_tvreport_co_kr': {
        'date': ("div", {'class': "line-txt-box"}),
        'title': ("h1", ),
        'text': ("div", {'class': "news-article"}),
        'decompose': (['figure', 'style', 'script','editor','subtitle','img','copy','banner'])
    },

    'www_doctorsnews_co_kr': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','editor','emoji','head-sub','tag','copy','banner'])
    },

    'www_sportsq_co_kr': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','editor','subtitle','tag','copy','banner'])
    },

    'www_econotelling_com': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','editor','head-sub','tag','copy','banner'])
    },

    'www_tvdaily_co_kr': {
        'date': ("font", {'class': "read_time"}),
        'title': ("font", {'class': "read_title"}),
        'text': ("div", {'class': "read"}),
        'decompose': (['figure', 'style', 'script','editor','head-sub','tag','copy','banner'])
    },

    'www_pdjournal_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','editor','head-sub','tag','copy','banner'])
    },

    'www_insnews_co_kr': {
        'date': ("p", ),
        'title': ("font", {'class': "headline"}),
        'text': ("font", {'class': "body_news"}),
        'decompose': (['figure', 'style', 'script','editor','head-sub','tag','copy','banner'])
    },

    'www_spotvnews_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','editor','head-sub','tag','copy','banner'])
    },

    'www_koit_co_kr': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','editor','head-sub','tag','copy','banner'])
    },

    'goodnews1_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script','editor','head-sub','tag','copy','adlink','adsby','banner'])
    },

    'sports_donga_com': {
        'date': ("div", {'class': "article_tit"}),
        'title': ("h1", {'class': "tit"}),
        'text': ("div", {'class': "article_word"}),
        'decompose': (['figure', 'style', 'script','editor','head-sub','tag','copy','sub_ad','banner'])
    },

    'www_sporbiz_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'kr_aving_net': {
        'date': ("div", {'class': "view-info"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'www_ifm_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'www_newscham_net': {
        'date': ("div", {'class': "byline"}),
        'title': ("h1", {'class': "title"}),
        'text': ("div", {'id': "news-article-content"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'www_viewsnnews_com': {
        'date': ("time", ),
        'title': ("h3", ),
        'text': ("div", {'class': "content"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'www_newstree_kr': {
        'date': ("div", {'class': "viewTitle"}),
        'title': ("h1", ),
        'text': ("div", {'id': "article"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'www_docdocdoc_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script', 'tem-type-8'])
    },

    'www_asiaa_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script', 'tem-type-8'])
    },

    'www_worldkorean_net': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script', 'copyright', 'editors'])
    },

    'www_fintechpost_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script', 'copyright', 'editors'])
    },

    'www_techm_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script', 'copyright', 'editors'])
    },

    'www_cfnews_kr': {
        'date': ("span", {'class': "date"}),
        'title': ("div", {'class': "newstitle"}),
        'text': ("div", {'id': "newscontent"}),
        'decompose': (['figure', 'style', 'script', 'copyright', 'editors'])
    },

    'www_ekoreanews_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script', 'copyright', 'editors'])
    },

    'www_ildaro_com': {
        'date': ("div", {'class': "writer_time"}),
        'title': ("h1", {'class': "read_title"}),
        'text': ("div", {'id': "textinput"}),
        'decompose': (['figure', 'style', 'script', 'img_caption', 'copyright', 'editors'])
    },

    'www_goal_com': {
        'date': ("div", {'class': "article_meta__RroSE"}),
        'title': ("h1", {'class': "article_title__9p8Mp"}),
        'text': ("div", {'class': "article-body_body__ASOmp body"}),
        'decompose': (['figure', 'style', 'script', 'img_caption', 'copyright', 'editors'])
    },


    'www_mediajeju_com': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script', 'head-sub','copyright', 'editors'])
    },

    'www_agrinet_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script', 'head-sub','copyright', 'editors'])
    },

    'www_newsworker_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script', 'head-sub','copyright', 'editors'])
    },

    'www_cnbnews_com': {
        'date': ("p", {'class': "arvdate"}),
        'title': ("h2", {'class': "article_title"}),
        'text': ("div", {'id': "news_body_area"}),
        'decompose': (['figure', 'style', 'script', 'head-sub','copyright', 'editors'])
    },

    'www_newsen_com': {
        'date': ("td", {'style': "padding:10px;", 'align': 'right'}),
        'title': ("span", {'class': "art_title"}),
        'text': ("div", {'id': "CLtag"}),
        'decompose': (['figure', 'style', 'script', 'head-sub','copyright'])
    },

    'www_digitaltoday_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script', 'head-sub','copyright'])
    },

    'www_thescoop_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script', 'head-sub','copyright'])
    },

    'www_kihoilbo_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['padding-top:5px;', 'figure', 'style', 'script', 'head-sub','copyright'])
    },

    'www_nongaek_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script', 'head-sub','copyright'])
    },

    'tenasia_hankyung_com': {
        'date': ("div", {'class': "view-info"}),
        'title': ("h1", {'class': "news-tit"}),
        'text': ("div", {'id': "article-body"}),
        'decompose': (['figure', 'style', 'script', 'head-sub','copyright'])
    },

    'www_lawissue_co_kr': {
        'date': ("span", {'class': "date"}),
        'title': ("h2", ),
        'text': ("div", {'class': "article detailCont"}),
        'decompose': (['mimg', 'style', 'script', 'head-sub','copyright'])
    },

    'www_worklaw_co_kr': {
        'date': ("ul", {'class': "view_wrap"}),
        'title': ("h3", ),
        'text': ("li", {'id': "contents_Area"}),
        'decompose': (['font-size:11px;', 'style', 'script', 'head-sub','copyright'])
    },

    'www_knnews_co_kr': {
        'date': ("div", {'class': "cont_tit"}),
        'title': ("h1", {'class': "h1_tex"}),
        'text': ("li", {'id': "content_li"}),
        'decompose': (['byline', 'photo', 'style', 'script', 'head-sub','copyright'])
    },

    'www_jjn_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['byline', 'figure', 'style', 'script', 'head-sub','copyright'])
    },

    'www_hidoc_co_kr': {
        'date': ("span", {'class': "date"}),
        'title': ("h2", {'class': "article_tit"}),
        'text': ("div", {'class': "article_body size2"}),
        'decompose': (['em', 'img', 'figure', 'style', 'script', 'head-sub','copyright'])
    },

    'www_yakup_com': {
        'date': ("div", {'class': "date_con"}),
        'title': ("div", {'class': "stitle_con"}),
        'text': ("div", {'class': "text_article_con"}),
        'decompose': (['figure', 'style', 'script', 'head-sub','copyright'])
    },

    'www_ccdailynews_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script', 'head-sub','copyright'])
    },

    'www_thebigdata_co_kr': {
        'date': ("div", {'class': "vctlt01"}),
        'title': ("h1", ),
        'text': ("div", {'class': "vcc01 news_article"}),
        'decompose': (['text-align:right;', 'font-weight:700;color:#aaa;padding:0px', 'figure', 'style', 'script', 'head-sub','copyright'])
    },

    'www_veritas-a_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script', 'head-sub','copyright'])
    },

    'www_idaegu_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script', 'head-sub','copyright'])
    },

    'www_insidevina_com': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['editors', 'tag-group', 'figure', 'style', 'script', 'head-sub','copyright'])
    },

    'www_radiokorea_com': {
        'date': ("span", {'class': "article-info"}),
        'title': ("h1", {'class': "article-title"}),
        'text': ("div", {'id': "news_content"}),
        'decompose': (['figure', 'style', 'script', 'head-sub','copyright'])
    },

    'www_jndn_com': {
        'date': ("font", {'class': "read_time"}),
        'title': ("font", {'class': "read_title"}),
        'text': ("div", {'id': "content"}),
        'decompose': (['read_title', 'read_time', 'margin-top:20px;text-align:right', 'figure', 'style', 'script', 'head-sub','copyright'])
    },

    'www_dailymedi_com': {
        'date': ("div", {'class': "info"}),
        'title': ("div", {'class': "view_subject"}),
        'text': ("div", {'class': "arti"}),
        'decompose': (['repoart', 'reporter', 'figure', 'style', 'script', 'head-sub','copyright'])
    },

    'www_jibs_co_kr': {
        'date': ("div", {'class': "pull-left m-t-md"}),
        'title': ("div", {'class': "col-xs-12 articles-detail-title m-t-sm p-h-xs border-bottom"}),
        'text': ("div", {'class': "col-xs-12 p-h-sm articles-detail-content"}),
        'decompose': (['figure', 'style', 'script', 'head-sub','copyright'])
    },

    'kor_theasian_asia': {
        'date': ("span", {'class': "meta-date"}),
        'title': ("h1", {'class': "entry-title"}),
        'text': ("div", {'class': "entry-content clearfix"}),
        'decompose': (['related', 'share', 'profile', 'figure', 'style', 'script', 'head-sub','copyright'])
    },

    'www_idomin_com': {
        'date': ("ul", {'class': "article-info-label"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script', 'head-sub','copyright'])
    },

    'www_public25_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script', 'head-sub','copyright'])
    },

    'www_newsway_co_kr': {
        'date': ("div", {'class': "view-date"}),
        'title': ("h1", {'class': "headline"}),
        'text': ("div", {'class': "view-area"}),
        'decompose': (['-tag', 'taboola', 'comment', 'ad-list', 'bottom', 'figure', 'style', 'script', 'copyright'])
    },

    'www_dailynk_com': {
        'date': ("span", {'class': "td-post-date"}),
        'title': ("h1", {'class': "entry-title"}),
        'text': ("div", {'class': "td-post-content tagdiv-type"}),
        'decompose': (['figure', 'style', 'script', 'copyright'])
    },

    'news_lghellovision_net': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script', 'copyright'])
    },

    'www_newsprime_co_kr': {
        'date': ("div", {'class': "arvdate"}),
        'title': ("h2", {'class': "title"}),
        'text': ("div", {'id': "news_body_area"}),
        'decompose': (['imgframe', 'figure', 'style', 'script', 'copyright'])
    },

    'www_newsnjoy_or_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['text-align: right;', 'color:#c0392b;', 'figure', 'style', 'script', 'copyright'])
    },

    'www_iminju_net': {
        'date': ("ul", {'class': "article-info-label"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script', 'copyright'])
    },

    'www_jejusori_net': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['color:#2980b9;', 'figure', 'style', 'script', 'copyright'])
    },

    'www_dtnews24_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'style', 'script', 'copyright'])
    },

    'www_segyebiz_com': {
        'date': ("div", {'class': "col-half text-right"}),
        'title': ("h1", {'class': "article-title"}),
        'text': ("div", {'class': "article-body"}),
        'decompose': (['footer', 'figure', 'script', 'copyright'])
    },

    'www_00news_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['figure', 'script', 'copyright'])
    },

    'www_goodnews1_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['style', 'figure', 'script', 'copyright'])
    },

    'www_aflnews_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['style', 'figure', 'script', 'copyright'])
    },

    'www_womaneconomy_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['style', 'figure', 'script', 'copyright'])
    },

    'www_mygoyang_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['color:#e67e22;', 'strong', 'style', 'figure', 'script', 'copyright'])
    },

    'www_natv_go_kr': {
        'date': ("p", {'class': "sub_detail_date"}),
        'title': ("h3", {'class': "sub_detail_title"}),
        'text': ("div", {'class': "detail_cont"}),
        'decompose': (['open', 'strong', 'style', 'figure', 'script', 'copyright'])
    },

    'www_livesnews_com': {
        'date': ("ul", {'class': "art_info"}),
        'title': ("h2", ),
        'text': ("div", {'id': "news_body_area"}),
        'decompose': (['imgframe', 'strong', 'style', 'figure', 'script', 'copyright'])
    },

    'www_cine21_com': {
        'date': ("div", {'class': "by"}),
        'title': ("div", {'class': "news_tit"}),
        'text': ("div", {'id': "news_content"}),
        'decompose': (['img', 'style', 'figure', 'script', 'copyright'])
    },

    'www_gokorea_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['style', 'figure', 'script', 'copyright'])
    },

    'www_koreareport_co_kr': {
        'date': ("div", {'class': "article-info"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['style', 'figure', 'script', 'copyright'])
    },

    'ent_sbs_co_kr': {
        'date': ("div", {'class': "w_cth_info"}),
        'title': ("h1", {'class': "cth_title"}),
        'text': ("div", {'class': "w_ctma_text"}),
        'decompose': (['_tag', 'copy', 'style', 'figure', 'script', 'copyright'])
    },

    'www_jbsori_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['color:#16a085;', 'style', 'figure', 'script', 'copyright'])
    },

    'www_economytalk_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['style', 'figure', 'script', 'copyright'])
    },

    'www_beminor_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['style', 'figure', 'script', 'copyright'])
    },

    'www_kbsm_net': {
        'date': ("div", {'class': "view_head_info_date"}),
        'title': ("h2", ),
        'text': ("div", {'id': "view_content_body"}),
        'decompose': (['photo', 'figure', 'script', 'copyright'])
    },

    'kookbang_dema_mil_kr': {
        'date': ("div", {'class': "info"}),
        'title': ("h2", {'class': "article_title"}),
        'text': ("div", {'id': "article_body_view"}),
        'decompose': (['btn_area', 'author', 'strong', 'tbody', 'figure', 'script', 'copyright'])
    },

    'www_headlinejeju_co_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['head-sub', 'editors', 'tbody', 'figure', 'script', 'copyright'])
    },

    'newstapa_org': {
        'date': ("div", {'class': "flex-grow-1"}),
        'title': ("h3", {'class': "font-weight-bold entry-title"}),
        'text': ("div", {'id': "editor_fontsize"}),
        'decompose': (['head-sub', 'image', 'tbody', 'figure', 'script', 'copyright'])
    },

    'www_sentv_co_kr': {
        'date': ("div", {'class': "util-area"}),
        'title': ("h1", {'class': "title"}),
        'text': ("div", {'id': "newsView"}),
        'decompose': (['head-sub', 'image', 'tbody', 'figure', 'script', 'copyright'])
    },

    'www_kdfnews_com': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['head-sub', 'style',  'image', 'editors', 'figure', 'script', 'copyright'])
    },

    'www_ccnnews_co_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['columns', 'head-sub', 'style',  'image', 'editors', 'figure', 'script', 'copyright'])
    },

    'www_newstof_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h1", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['background:#eeeeee;border:1px', 'head-sub', 'style', 'editors', 'figure', 'script', 'copyright'])
    },

    'www_thekpm_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['head-sub', 'style', 'editors', 'figure', 'script', 'copyright'])
    },

    'nownews_seoul_co_kr': {
        'date': ("span", {'class': "vDate"}),
        'title': ("h1", {'class': "articleTitleTextDiv"}),
        'text': ("div", {'id': "articleContent"}),
        'decompose': (['head-sub', 'style', 'editors', 'photo', 'script', 'copyright'])
    },

    'www_jejunews_com': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['text-center', 'emoji', 'head-sub', 'style', 'editors', 'figure', 'script', 'copyright'])
    },

    'www_vop_co_kr': {
        'date': ("div", {'class': "article-info"}),
        'title': ("h1", ),
        'text': ("div", {'class': "contents"}),
        'decompose': (['style', 'editors', 'photo', 'script', 'copyright'])
    },

    'www_smarttoday_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['style', 'editors', 'figure', 'script', 'copyright'])
    },

    'news_koreanbar_or_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['style', 'editors', 'figure', 'script', 'copyright'])
    },

    'www_sisaweek_com': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['tem-custom', 'style', 'editors', 'figure', 'script', 'copyright'])
    },

    'www_sisamagazine_co_kr': {
        'date': ("ul", {'class': "infomation"}),
        'title': ("h3", {'class': "heading"}),
        'text': ("article", {'id': "article-view-content-div"}),
        'decompose': (['style', 'editors', 'figure', 'script', 'copyright'])
    },

    'news_maxmovie_com': {
        'date': ("div", {'class': "Title__SubBox-sc-1xqy65w-3 bDAHNJ"}),
        'title': ("h3", ),
        'text': ("div", {'class': "mainNews"}),
        'decompose': (['style', 'editors', 'figure', 'script', 'copyright'])
    },

    'www_kyosu_net': {
        'date': ("div", {'class': "info-text"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'id': "article-view-content-div"}),
        'decompose': (['article-head-sub','tag-group','view-copyright','view-editors','figure', 'style', 'script'])
    },

    'www_cts_tv': {
        'date': ("td", {'colspan': "2"}),
        'title': ("div", {'class': "text"}),
        'text': ("td", {'class': "first body"}),
        'decompose': (['figure', 'style', 'script'])
    },

    'slownews_kr': {
        'date': ("div", {'class': "entry-meta entry-meta-divider-customicon"}),
        'title': ("h1", {'class': "entry-title"}),
        'text': ("div", {'id': "pavo_contents"}),
        'decompose': (['kt-infobox-textcontent','wp-block-rank-math-toc-block','wp-block-quote','nav','wp-block-heading','figure', 'script'])
    },

    'www_idaegu_co_kr': {
        'date': ("ul", {'class': "no-bullet auto-marbtm-0 line-height-6"}),
        'title': ("div", {'class': "article-head-title"}),
        'text': ("div", {'class': "news_text"}),
        'decompose': (['kt-infobox-textcontent','wp-block-rank-math-toc-block','wp-block-quote','nav','wp-block-heading','figure', 'script'])
    },


}


class NewsCrawler:
    def __init__(self):
        chrome_options = Options()
        # chrome_options.add_argument("--ignore-certificate-errors")
        # chrome_options.add_argument("--ssl-protocol=any")
        # chrome_options.add_argument("--ignore-ssl-errors=true")
        chrome_options.add_argument("--headless")  # 헤드리스 모드 활성화
        # chrome_options.add_argument("--disable-features=SameSiteByDefaultCookies,CookiesWithoutSameSiteMustBeSecure")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def crawl(self, url, site_key):
        # 기본 크롤러를 호출하는 경우
        if site_key in sites_config:
            return defalt_crawler(self.driver, url, site_key)
        elif site_key in sites_config_decompose:
            return defalt_crawler_decompose(self.driver, url, site_key)
        else:
            # 동적으로 사이트 특화 크롤러 호출
            function_name = f'{site_key}_crawler'
            crawler_function = globals().get(function_name)
            if crawler_function:
                return crawler_function(self.driver, url)
            else:
                print(f"No crawler function or default config found for {site_key} : {url}")
                return None

    def close(self):
        self.driver.quit()

####### 유형이 같은 URL  ###################
def defalt_crawler(driver, url, site_key):
    config = sites_config[site_key]
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find(*config['date'])
    date = date_element.get_text(strip=True) if date_element else None
    
    title_element = soup.find(*config['title'])
    title_text = title_element.get_text(strip=True) if title_element else None
    
    text_elements = soup.find_all(*config['text'])
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)

    return date, title_text, full_text


def defalt_crawler_decompose(driver, url, site_key):
    config = sites_config_decompose[site_key]
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find(*config['date'])
    date = date_element.get_text(strip=True) if date_element else None
    
    title_element = soup.find(*config['title'])
    title_text = title_element.get_text(strip=True) if title_element else None
    
    keywords = [*config['decompose']]
    exclude_elements_with_keywords(soup, keywords)
    text_elements = soup.find(*config['text'])  # find_all or find
#    print(text_elements)
#    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text



############# 유형이 다른 URL ###################

# 머니투데이
def news_mt_co_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find("li", class_="date")
    date = date_element.get_text(strip=True) if date_element else None
        
    title_text_element = soup.find("h1", class_="subject")
    title_text = title_text_element.contents[0] if title_text_element else 'No title found'
    
    
    text_body = soup.find("div", id="textBody")
    for unwanted_tag in text_body.find_all(["script", "style", "div", "table", "b"]):
        unwanted_tag.decompose()
    full_text = ' '.join(text_body.stripped_strings)
    
    return date, title_text, full_text

# 머니투데이
def www_mt_co_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find("li", class_="date")
    date = date_element.get_text(strip=True) if date_element else None
        
    title_text_element = soup.find("h1", class_="subject")
    title_text = title_text_element.contents[0] if title_text_element else 'No title found'
    
    
    text_body = soup.find("div", id="textBody")
    for unwanted_tag in text_body.find_all(["script", "style", "div", "table", "b"]):
        unwanted_tag.decompose()
    full_text = ' '.join(text_body.stripped_strings)
    
    return date, title_text, full_text

# 중앙일보
def www_joongang_co_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find("p", class_="date")
    date = date_element.get_text(strip=True) if date_element else None
        
    title_text_element = soup.find("h1", class_="headline")
    title_text = title_text_element.get_text(strip=True) if title_text_element else None
    
    paragraphs = soup.select('#article_body p[data-divno]')
    full_text = ' '.join(paragraph.get_text(strip=True) for paragraph in paragraphs)
    
    return date, title_text, full_text

# 네이버뉴스
def news_naver_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_span = soup.find("span", class_="_ARTICLE_DATE_TIME")
    date_first = date_span["data-date-time"] if date_span else "Date not found"
    date_span = soup.find("span", class_="_ARTICLE_MODIFY_DATE_TIME")
    date_late = date_span["data-modify-date-time"] if date_span else "Date not found"
    date = " ".join([date_first, date_late])
        
    title_text_element = soup.find("h2", id="title_area")
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    for desc in soup.find_all("em", class_="img_desc"):
        desc.decompose()
    for span in soup.find_all("span"):
        span.decompose()
    text_elements = soup.find("div", id="newsct_article")
    text_fragments = []
    def handle_element(element):
        if isinstance(element, NavigableString):
            text = str(element).strip()
            # ▶, @ 기호를 포함하는 텍스트 조각을 제거(광고, 이메일 제거)
            if '▶' not in text and '@' not in text and 'ⓒ' not in text:
                text_fragments.append(text)
        elif element.name == 'br':
            # <br> 태그를 만날 때마다 개행 문자로 대체합니다.
            text_fragments.append('')
        else:
            for child in element.children:
                handle_element(child)
    handle_element(text_elements)
    full_text = ' '.join(fragment for fragment in text_fragments if fragment)
    
    return date, title_text, full_text

def n_news_naver_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_span = soup.find("span", class_="_ARTICLE_DATE_TIME")
    date_first = date_span["data-date-time"] if date_span else "Date not found"
    date_span = soup.find("span", class_="_ARTICLE_MODIFY_DATE_TIME")
    date_late = date_span["data-modify-date-time"] if date_span else "Date not found"
    date = " ".join([date_first, date_late])
        
    title_text_element = soup.find("h2", id="title_area")
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    for desc in soup.find_all("em", class_="img_desc"):
        desc.decompose()
    for span in soup.find_all("span"):
        span.decompose()
    text_elements = soup.find("div", id="newsct_article")
    text_fragments = []
    def handle_element(element):
        if isinstance(element, NavigableString):
            text = str(element).strip()
            # ▶, @ 기호를 포함하는 텍스트 조각을 제거(광고, 이메일 제거)
            if '▶' not in text and '@' not in text and 'ⓒ' not in text:
                text_fragments.append(text)
        elif element.name == 'br':
            # <br> 태그를 만날 때마다 개행 문자로 대체합니다.
            text_fragments.append('')
        else:
            for child in element.children:
                handle_element(child)
    handle_element(text_elements)
    full_text = ' '.join(fragment for fragment in text_fragments if fragment)
    
    return date, title_text, full_text

# imbc
def www_imbc_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    iframe = driver.find_element(By.ID, "hbbs_newshigh_02")
    iframe_src = iframe.get_attribute('src')
    response = requests.get(iframe_src)
    soup = BeautifulSoup(response.content, 'html.parser')

    date_element = soup.find("span", id="rptView_ctl00_lblDateInfo")
    date = date_element.get_text(strip=True) if date_element else None
        
    title_text_element = soup.find("span", id="rptView_ctl00_lblTitle")
    title_text = title_text_element.get_text(strip=True) if title_text_element else None
    
    paragraphs = soup.find("span", id="rptView_ctl00_lblContent")
    full_text = ' '.join(paragraph.get_text(strip=True) for paragraph in paragraphs)
    
    return date, title_text, full_text

# 다음뉴스
def news_v_daum_net_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_elements = soup.find_all("span", class_="num_date")
    date = ', '.join(date_element.get_text(strip=True) for date_element in date_elements)
        
    title_element = soup.find("h3", class_="tit_view")
    title_text = title_element.get_text(strip=True) if title_element else 'No title found'
    
    keywords = []
    text_elements = soup.find('div', class_='article_view')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

# CBS뉴스
def www_cbs_co_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find_all("td", class_="bd_menu_content")
    date = date_element[3].get_text(strip=True) if date_element[3] else 'No title found'
        
    title_element = soup.find("td", class_="bd_menu_content")
    title_text = title_element.get_text(strip=True) if title_element else 'No title found'
    
    keywords = ['인터뷰', "프로그램명 'CBS라디오"]
    text_elements = soup.find("td", class_="bd_article")
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

# 서울신문
def www_seoul_co_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find_all("div", class_="body13 color500")
    date_first = date_element[0].get_text(strip=True) if date_element[0] else 'No title found'
    date_last = date_element[1].get_text(strip=True) if date_element[1] else 'No title found'
    date = ', '.join([date_first, date_last])
        
    title_element = soup.find("h1", class_="h38")
    title_text = title_element.get_text(strip=True) if title_element else 'No title found'
    
    keywords = ['body14 color600', 'stit', 'v_photoarea', 'margin-top:30px;margin-bottom:30px;clear:both;']
    text_elements = soup.find("div", class_="viewContent body18 color700")
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

# 한국경제
def www_hankyung_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find_all("span", class_="item")
    date_first = date_element[0].get_text(strip=True) if date_element[0] else 'No title found'
    date_last = date_element[1].get_text(strip=True) if date_element[1] else 'No title found'
    date = ', '.join([date_first, date_last])
        
    title_element = soup.find("h1", class_="headline")
    title_text = title_element.get_text(strip=True) if title_element else 'No title found'
    
    keywords = ['a', 'figure', 'ad-wrap']
    text_elements = soup.find("div", class_="article-body")
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

# 한국경제
def news_hankyung_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find_all("span", class_="item")
    date_first = date_element[0].get_text(strip=True) if date_element[0] else 'No title found'
    date_last = date_element[1].get_text(strip=True) if date_element[1] else 'No title found'
    date = ', '.join([date_first, date_last])
        
    title_element = soup.find("h1", class_="headline")
    title_text = title_element.get_text(strip=True) if title_element else 'No title found'
    
    keywords = ['a', 'figure', 'ad-wrap']
    text_elements = soup.find("div", class_="article-body")
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

# 노컷뉴스
def www_nocutnews_co_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find("ul", class_="bl_b").find_all("li")
    for li in date_element:
        if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', li.text.strip()):  # YYYY-MM-DD HH:MM 포맷 확인
            date = li.text.strip()
            break
    else:
        date = 'No date found'

    element = soup.find("div", class_="h_info")
    title_element = element.find("h2")
    title_text = title_element.get_text(strip=True) if title_element else 'No title found'

    keywords = ['strong', 'fr-img-wrap']
    text_elements = soup.find("div", id="pnlContent")
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

# 이데일리
def www_edaily_co_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('div', class_='dates')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    title_text_element = soup.find("div", class_="news_titles").find('h1')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'

    keywords = ['table', 'caption', 'second_text']
    text_elements = soup.find("div", class_="news_body")
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

# 이데일리
def starin_edaily_co_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('div', class_='dates')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    title_text_element = soup.find("div", class_="news_titles").find('h1')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'

    keywords = ['table', 'caption', 'second_text']
    text_elements = soup.find("div", class_="news_body")
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

# tbs뉴스
def tbs_seoul_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('p', class_='bg3')
    date = date_element.get_text(strip=True) if date_element else 'No date found'
        
    title_text_element = soup.find("div", class_="sub2-title1").find('strong')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['sub2-text1 gray mgtb40']
    text_elements = soup.find("ul", class_="sub2-text1")
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

# 
def www_korea_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('div', class_='info')
    date = date_element.get_text(strip=True) if date_element else 'No date found'
        
    title_text_element = soup.find("div", class_="article_head").find('h1')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    paragraphs = soup.find_all('div', class_='article_body')
    full_text = ' '.join(paragraph.get_text(strip=True) for paragraph in paragraphs)
    
    return date, title_text, full_text

# 레이더P
def raythep_mk_co_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('li', class_='lasttime')
    date = date_element.get_text(strip=True) if date_element else 'No date found'
        
    title_text_element = soup.find("div", class_="view_title").find('h3')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['image', 'margin']
    text_elements = soup.find('div', id='article_body')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

# 한겨레
def www_hani_co_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find_all('li', class_='ArticleDetailView_dateListItem__6uf9E')
    date_first = date_element[0].get_text(strip=True) if date_element[0] else 'No title found'
    date_last = date_element[1].get_text(strip=True) if date_element[1] else 'No title found'
    date = ', '.join([date_first, date_last])

    title_text_element = soup.find("h3", class_="ArticleDetailView_title__fDOCx")
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['linkstyle-u', 'figcaption']
    text_elements = soup.find('div', class_='article-text')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

# 뉴스1
def news1_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('div', class_='info')
    date = date_element.get_text(strip=True) if date_element else 'No date found'
        
    title_text_element = soup.find("div", class_="title").find('h2')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['table', 'margin']
    text_elements = soup.find('div', class_='detail sa_area')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

# 뉴스1
def www_news1_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('div', class_='info')
    date = date_element.get_text(strip=True) if date_element else 'No date found'
        
    title_text_element = soup.find("div", class_="title").find('h2')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['table', 'margin']
    text_elements = soup.find('div', class_='detail sa_area')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

# 동아일보
def www_donga_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find_all('span', {'aria-hidden': 'true'})
    date_last = date_element[0].get_text(strip=True) if date_element[0] else 'No date found'
    date_first = date_element[1].get_text(strip=True) if date_element[1] else 'No update found'
    date = ', '.join(['입력:' + date_first] + ['업데이트:' + date_last])

    title_text_element = soup.find("section", class_="head_group").find('h1')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['img', 'sub_tit', '"view_m_ad']
    text_elements = soup.find('section', class_='news_view')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def news_donga_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find_all('span', {'aria-hidden': 'true'})
    date_last = date_element[0].get_text(strip=True) if date_element[0] else 'No date found'
    date_first = date_element[1].get_text(strip=True) if date_element[1] else 'No update found'
    date = ', '.join(['입력:' + date_first] + ['업데이트:' + date_last])

    title_text_element = soup.find("section", class_="head_group").find('h1')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['img', 'sub_tit', '"view_m_ad']
    text_elements = soup.find('section', class_='news_view')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

# 아시아경제
def view_asiae_co_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('div', class_='date_box')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    title_text_element = soup.find("div", class_="area_title").find('h1')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['related', 'ad_', 'mainnews_add', 'font-weight:bold;', 'fb-root', 'head', 'photo', 'ad_mid', 'e_article', 'art', 'add_', 'prohibition', 'fb-quote']
    text_elements = soup.find('div', class_='article fb-quotable')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

# 아시아경제
def www_asiae_co_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('div', class_='date_box')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    title_text_element = soup.find("div", class_="area_title").find('h1')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['related', 'ad_', 'mainnews_add', 'font-weight:bold;', 'fb-root', 'head', 'photo', 'ad_mid', 'e_article', 'art', 'add_', 'prohibition', 'fb-quote']
    text_elements = soup.find('div', class_='article fb-quotable')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

# 국제신문
def www_kookje_co_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('span', class_='f_news_date')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    title_text_element = soup.find("div", class_="news_title").find('h1')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['table']
    text_elements = soup.find('div', class_='news_article')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def www_seouland_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('div', class_='datebox')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    title_text_element = soup.find("header", class_="article_head").find('h1')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['strong', 'image', 'a']
    text_elements = soup.find('div', class_='article_body')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def travel_donga_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('p', class_='title_foot')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    title_text_element = soup.find("div", class_="article_title").find('h2')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['strong', 'articlePhoto']
    text_elements = soup.find('div', class_='article_txt')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def the300_mt_co_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('span', class_='date')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    title_text_element = soup.find("div", class_="article_header").find('h1')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['article_photo']
    text_elements = soup.find('div', id='textBody')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def m_news_naver_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('span', class_='date')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    title_text_element = soup.find("div", class_="article_header").find('h1')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['article_photo']
    text_elements = soup.find('div', id='textBody')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def www_mbn_co_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('span', class_='time')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    title_text_element = soup.find("div", class_="box01").find('h1')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['player', 'script', 'padding-left']
    text_elements = soup.find('div', class_='detail')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def www_pressian_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('span', class_='date')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    title_text_element = soup.find("div", class_="view_header").find('p')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['color:hsl(243,59%,48%);', 'article_ad', 'style', 'figure', 'copyright', 'script']
    text_elements = soup.find('div', class_='article_body')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def mbn_mk_co_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('span', class_='time')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    title_text_element = soup.find("div", class_="box01").find('h1')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['tbody', 'strong', 'script', 'figure', 'copy']
    text_elements = soup.find('div', class_='detail')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def www_asiatoday_co_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('span', class_='wr_day')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    title_text_element = soup.find("div", class_="section_top_box").find('h3')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['tbody', 'strong', 'script', 'figure', 'copy']
    text_elements = soup.find('div', class_='news_bm')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def monthly_chosun_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('span', class_='wr_day')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    title_text_element = soup.find("div", class_="title_title").find('h3')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['ad2', 'adsbygoogle', 'tbody', 'strong', 'script', 'figure', 'copy']
    text_elements = soup.find('div', id='id_articleBody')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def www_jnilbo_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('ul', id='byline')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    keywords = ['adttl2', 'byline', 'social']
    title_text_element = soup.find("div", id="adttl")
    exclude_elements_with_keywords(title_text_element, keywords)
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['margin-top:20px;text-align:right', 'ad-box', 'copyright', 'figure', 'style', 'script']
    text_elements = soup.find('div', id='content')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def www_ifs_or_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('ul', class_='divider-sm list--inline text-caption--em text-dark--air board__view-datetime')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    
    title_text_element = soup.find("h2", class_="divider-sm text-headline4--em text-dark board__view-title").find('strong')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['margin-top:20px;text-align:right', 'ad-box', 'copyright', 'figure', 'style', 'script']
    text_elements = soup.find('div', id='bo_v_con')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def www_ilyosisa_co_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('ul', class_='art_info')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    
    title_text_element = soup.find("div", class_="art_top").find('h2')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['imgframe', 'tbody', 'summary', 'figure', 'script']
    text_elements = soup.find('div', id='news_body_area')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def www_boannews_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('div', id='news_util')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    
    title_text_element = soup.find("div", id="news_title02").find('h1')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['font-weight:400;color:#000000;', 'a', 'p', 'news_image', 'tbody', 'summary', 'figure', 'script']
    text_elements = soup.find('div', id='news_content')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def www_ddanzi_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('p', id='time')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    
    title_text_element = soup.find("div", class_="top_title").find('h1')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['baseline;', 'tbody', 'img', 'script']
    text_elements = soup.find('div', class_='read_content')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def www_naon_go_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('div', id='report_tit')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    
    title_text_element = soup.find("div", class_="report_tit").find('h2')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['strong','figure', 'style', 'script']
    text_elements = soup.find('div', class_='con_area')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def weekly_cnbnews_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('p', class_='arvdate')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    
    title_text_element = soup.find("div", class_="arvtitle").find('h2')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['font','figure', 'style', 'script']
    text_elements = soup.find('div', id='news_body_area')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def www_kpanews_co_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('p', class_='t1 t_date')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    
    title_text_element1 = soup.find("div", class_="tbl_head")
    title_text_element2 = title_text_element1.find('p', class_="h1")
    title_text = title_text_element2.get_text(strip=True) if title_text_element2 else 'No title found'
    
    keywords = ['nrbox', 'article_ad', 'article_s', 'bbs_img', 'style', 'script', 'head-sub','copyright']
    text_elements = soup.find('div', class_='bbs_cont inr-c2')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def www_ktv_go_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('p', class_='date')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    
    title_text_element = soup.find('div', class_="lft").find('h2')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['copyright', 'figure']
    text_elements = soup.find('div', class_='article zoominout')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def medicalworldnews_co_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('div', class_='registModifyDate')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    
    title_text_element = soup.find('div', class_="titleWrap boxPointColor").find('strong')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['keyword', 'related', 'style', 'figure', 'script', 'copyright']
    text_elements = soup.find('div', id='viewContent')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def www_koreatimes_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('span', id='print_arti_info')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    
    title_text_element = soup.find('div', class_="tit_arti").find('h4')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['writer', 'sub_tit', 'photo', 'figure', 'script', 'copyright']
    text_elements = soup.find('div', id='print_arti')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def www_medipana_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('span', class_='r')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    
    title_text_element = soup.find('div', class_="tit").find('p')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['style', 'editors', 'figure', 'script', 'copyright']
    text_elements = soup.find('div', class_='artice_cont_box')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def www_irobotnews_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('div', class_='View_Time')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    title_text_element = soup.find('div', class_="View_Title").find('strong')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['tbody', 'style', 'editors', 'figure', 'script', 'copyright']
    text_elements = soup.find('td', class_='view_r')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def mdtoday_co_kr_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('div', class_='viewTitle')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    title_text_element = soup.find('div', class_='viewTitle').find('h3')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['color:#494949;', 'adsby', 'summary', 'tbody', 'script', ]
    text_elements = soup.find('div', id='articleBody')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def www_sportsworldi_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('p', class_='viewInfo')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    title_text_element = soup.find('h3', id='title_sns')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['precis', 'summary', 'figure', 'script', 'style', ]
    text_elements = soup.find('div', id='article_txt')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def www_gobalnews_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('div', class_='View_Time')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    title_text_element = soup.find('div', class_='View_Title').find('strong')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['tbody', 'summary', 'figure', 'script', 'style', ]
    text_elements = soup.find('td', class_='view_r')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def www_koreadaily_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('p', class_='date-bold article-date-bold')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    title_text_element = soup.find('h1', class_='view-article-title')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['title', 'summary', 'figure', 'script', 'style', ]
    text_elements = soup.find('div', id='article_body')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def www_pckworld_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('div', id='newstime')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    title_text_element = soup.find('font', class_='read_title')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['title', 'margin-top:5px', 'bar', 'tbody', 'text-align:right', 'newstime']
    text_elements = soup.find('div', id='content')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def www_segyefn_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('div', class_='article-meta')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    title_text_element = soup.find('h1', class_='article-title')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['tbody', 'newstime', 'footer', 'style', 'script']
    text_elements = soup.find('div', class_='article-body')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def www_ceoscoredaily_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('div', class_='util_box')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    
    title_text_element = soup.find('div', class_="article_head type_05").find('p')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['ab_body_byline','copyright','figure', 'style', 'script']
    text_elements = soup.find('div', class_='article_content')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text

def www_medipana_com_crawler(driver, url):
    driver.get(url)
    time.sleep(1)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    
    date_element = soup.find('span', class_='r')
    date = date_element.get_text(strip=True) if date_element else 'No date found'

    
    title_text_element = soup.find('div', class_="tit").find('p')
    title_text = title_text_element.get_text(strip=True) if title_text_element else 'No title found'
    
    keywords = ['style', 'editors', 'figure', 'script', 'copyright']
    text_elements = soup.find('div', class_='artice_cont_box')
    full_text = ''
    exclude_elements_with_keywords(text_elements, keywords)
    full_text = ' '.join(element.get_text(strip=True) for element in text_elements)
    
    return date, title_text, full_text







####### 주어진 키워드를 포함하는 클래스 이름을 검사(제거)하는 내부 함수 #######
# def exclude_elements_with_keywords(soup, keywords):
    
#     def contains_keyword(class_name):
#         if class_name:
#             return any(keyword in class_name for keyword in keywords)
#         return False
    
#     for element in soup.find_all(class_=contains_keyword):
#         element.decompose()

def exclude_elements_with_keywords(soup, keywords):
    if soup is None:
        return  # soup 객체가 None이면 함수 실행을 중단

    # 클래스, ID, 또는 태그 이름에 주어진 키워드가 포함되어 있는지 검사하는 내부 함수
    def contains_keyword(attribute_value):
        if attribute_value:
            return any(keyword in attribute_value for keyword in keywords)
        return False
    
    # 클래스나 ID가 주어진 키워드를 포함하는 모든 요소 찾아 제거
    for element in soup.find_all(True, class_=contains_keyword):
        element.decompose()
    for element in soup.find_all(True, id=contains_keyword):
        element.decompose()
    for element in soup.find_all(True, style=contains_keyword):
        element.decompose()        
    
    # 주어진 키워드 목록에 해당하는 태그 이름을 가진 모든 요소 찾아 제거
    for keyword in keywords:
        for element in soup.find_all(keyword):
            element.decompose()

# def exclude_elements_with_keywords(soup, keywords):
#     if soup is None:
#         return

#     def contains_keyword(attribute_value):
#         # attribute_value가 None인 경우를 처리
#         if attribute_value is None:
#             return False
#         return any(keyword in attribute_value for keyword in keywords)

#     # 클래스, ID, 스타일 속성에 키워드가 포함된 요소 제거
#     for element in soup.find_all(True, class_=contains_keyword):
#         element.decompose()
#     for element in soup.find_all(True, id_=contains_keyword):
#         element.decompose()
#     for element in soup.find_all(True, style=contains_keyword):
#         element.decompose()

#     # 텍스트 내용에 키워드가 포함된 요소 제거
#     # soup 객체의 모든 자손 요소를 순회하면서 검사
#     for element in soup.descendants:
#         if element.name and any(keyword in element.get_text() for keyword in keywords):
#             element.decompose()







# # 사용 예
# if __name__ == '__main__':
#     # KBS 뉴스 URL 예시
#     kbs_url = 'https://news.kbs.co.kr/news/view.do?ncd=1234567'
#     date, title, full_text = defalt_crawler(kbs_url, 'kbs')
#     print(f"Date: {date}\nTitle: {title}\nFull Text: {full_text}")
    
#     # 중앙일보 URL 예시
#     joongang_url = 'https://www.joongang.co.kr/article/123456789'
#     date, title, full_text = defalt_crawler(joongang_url, 'joongang')
#     print(f"Date: {date}\nTitle: {title}\nFull Text: {full_text}")