import json

json_input = './raw_data_10days.json'
with open(json_input, 'r', encoding='utf8') as f:
    data = json.load(f)

list_video = []

for key in data:
    curr_vid = data[key]
    after_format = {}
    after_format['id'] = curr_vid['id']
    after_format['text'] = curr_vid['desc']
    after_format['createTime'] = curr_vid['createTime']
    after_format['authorMeta'] = {
        "id": curr_vid['author']['id'],
        "secUid": curr_vid['author']['secUid'],
        "name": curr_vid['author']['nickname'],
        "nickName": curr_vid['author']['nickname'],
        "verified": curr_vid['author']['verified'],
        "signature": curr_vid['author']['signature'],
        "avatar": curr_vid['author']['avatarLarger']
    }
    after_format['musicMeta'] = {
        "musicId": curr_vid['music']['id'],
        "musicName": curr_vid['music']['title'],
        "musicAuthor": curr_vid['music']['authorName'],
        "musicOriginal": curr_vid['music']['original'],
        "playUrl": curr_vid['music']['playUrl'],
        "coverThumb": curr_vid['music']['coverThumb'],
        "coverMedium": curr_vid['music']['coverMedium'],
        "coverLarge": curr_vid['music']['coverLarge'],
    }
    after_format['covers'] = {
        "default": curr_vid['video']['cover'],
        "origin": curr_vid['video']['originCover'],
        "dynamic": curr_vid['video']['dynamicCover'],
    }
    after_format['webVideoUrl'] = curr_vid['video']['playAddr']
    after_format['videoUrl'] = curr_vid['video']['downloadAddr']
    after_format['videoMeta'] = {
        "height": curr_vid['video']['height'],
        "width": curr_vid['video']['width'],
        "duration": curr_vid['video']['duration'],
    }
    after_format['diggCount'] = curr_vid['stats']['diggCount']
    after_format['shareCount'] = curr_vid['stats']['shareCount']
    after_format['playCount'] = curr_vid['stats']['playCount']
    after_format['commentCount'] = curr_vid['stats']['commentCount']
    list_hashtag = []
    try:
        if curr_vid["textExtra"]:
            for item in curr_vid["textExtra"]:
                list_hashtag.append(item['hashtagName'])
    except:
        pass
    after_format['hashtags'] = list_hashtag
    list_video.append(after_format)

dict_out = {"collector": list_video}

with open('data_tiktok_10days.json', 'w', encoding='utf8') as f:
    json.dump(dict_out, f, ensure_ascii=False, indent=4)