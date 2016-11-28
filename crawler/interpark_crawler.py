# -*- coding: utf-8 -*-
import requests

from bs4 import BeautifulSoup

"""
인터파크 티켓 뮤지컬 부분 크롤러로, max_rank (몇위 까지) 와 sort_type(정렬 순)으로 크롤링 가능.
sort_type : 1(금일 랭킹), 2(주간 랭킹순), 3(월간 랭킹), 4(상품명), 5(공연종료 임박순)
"""


def interpark_crawler(max_rank, sort_type=1):
    rank = 1

    url = 'http://ticket.interpark.com/TPGoodsList.asp?Ca=Mus&Sort=' + str(sort_type)
    source_code = requests.get(url)
    plain_text = source_code.text

    ticket_musical_soup = BeautifulSoup(plain_text, 'lxml')

    musical_list = ticket_musical_soup.select('span.fw_bold > a')

    for musical in musical_list:
        musical_url = 'http://ticket.interpark.com/' + musical.get('href')

        musical_source_code = requests.get(musical_url)
        musical_plain_text = musical_source_code.text

        musical_soup = BeautifulSoup(musical_plain_text, 'lxml')

        print(str(rank) + "위")

        # 뮤지컬 이름
        musical_title = musical_soup.find(id="IDGoodsName").text
        print("뮤지컬 제목 : ", musical_title)

        # 뮤지컬 부제
        musical_info_list = musical_soup.select('div.TabA_Info > ul.info_Li > li')

        if musical_info_list[0].text[0:2] == '부제':
            musical_subtitle = musical_info_list[0].text[2:]
        else:
            musical_subtitle = ''

        print('부제 : ', musical_subtitle)

        # 뮤지컬 공연 장소, 뮤지컬 공연 기간
        musical_info_table = musical_soup.select('div.Data_infoarea > table > tr > td')

        for num, info in enumerate(musical_info_table):
            musical_info_table[num] = info.text

        musical_place = musical_info_table[5]

        # 42(기간 예매권), 52(하루 공연), 58(오픈런), 65(기간)
        musical_term_len = len(musical_info_table[8])
        if musical_term_len == 52:
            musical_term = musical_info_table[8][0:12]
        elif musical_term_len == 58:
            musical_term = musical_info_table[8][0:18]
        else:
            musical_term = musical_info_table[8][0:23]

        print("공연 장소 : ", musical_place)
        print("공연 기간 : ", musical_term)

        # 나이 제한, 러닝 타임
        musical_etc_tag = musical_soup.find('dd', attrs={'class': 'etc'})
        musical_etc_info_list = musical_etc_tag.text.split('|')

        for num, info in enumerate(musical_etc_info_list):
            musical_etc_info_list[num] = info.strip()

        # list[0] 장르, list[1] 러닝 타임, list[2] 나이 제한
        if len(musical_etc_info_list) == 3:
            musical_running_time = musical_etc_info_list[1]
            musical_age_req = musical_etc_info_list[2]

            print("나이 제한 : ", musical_age_req)
            print("러닝 타임 : ", musical_running_time)
        # list[0] 장르, list[1] 나이 제한
        else:
            musical_age_req = musical_etc_info_list[1]

            print("나이 제한 : ", musical_age_req)

        # 배우 리스트
        musical_member_list = musical_soup.select('li.members > div > a')

        print('배우 리스트')
        if musical_member_list:
            for member in musical_member_list:
                name = member.text

                if name == '더보기 ':
                    break

                member_link = member.get('href')
                print(name, member_link)
        else:
            print("-")

        # 뮤지컬 POSTER IMAGE
        poster_area = musical_soup.select('div.poster > img')
        if poster_area:
            print('POSTER 이미지 : ', poster_area[0].get('src'))

        # 뮤지컬 NOTICE IMAGE
        notice_area = musical_soup.select('div.Data_infoarea > p > img')

        if not notice_area:
            notice_area = musical_soup.select('div.Data_infoarea > img')

        if notice_area:
            notice_img = notice_area[0].get('src')
            print('NOTICE 이미지 : ', notice_img)

        # 뮤지컬 INFO IMAGE
        info_img_call_url = "http://ticket.interpark.com/Ticket/Goods/GoodsInfoHttpNew.asp?Flag=Detail&GoodsCode=" \
                            + musical_url[66:]

        info_img_code = requests.get(info_img_call_url)
        info_img_plain_text = info_img_code.text

        info_img_soup = BeautifulSoup(info_img_plain_text, 'lxml')

        info_img = info_img_soup.select('p > strong > img')

        if not info_img:
            info_img = info_img_soup.select('p > img')

        if not info_img:
            info_img = info_img_soup.select('img')

        if info_img:
            print('INFO 이미지 : ', info_img[0].get('src'))

        if max_rank == rank:
            break

        rank += 1


interpark_crawler(5, 1)
