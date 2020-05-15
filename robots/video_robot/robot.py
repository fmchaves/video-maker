def create_video(video_content: dict, dst_path: str):

    from moviepy.editor import ImageSequenceClip, TextClip, CompositeVideoClip
    import os   
    
    images = ImageSequenceClip(video_content['images'], durations=video_content['duration_images'])
    texts = []
    for i in range(len(video_content['sentences'])):    
        texts.append(
            TextClip(
                video_content['sentences'][i], 
                font='Amiri-Bold', 
                fontsize=video_content['font_size'][i], 
                color='yellow',
                bg_color='black').set_position(video_content['text_position'][i]).set_start(video_content['start_sentences_in'][i]).set_duration(video_content['duration_sentences'][i]))
    timeline = [images]
    timeline.extend(texts)
    final_clip = CompositeVideoClip(timeline)
    filename = os.path.join(dst_path, 'video.mp4')
    final_clip.write_videofile(filename, fps=2)

def insert_breaklines(sentence: str, max_words_per_line: int) -> str:

    words = sentence.split(' ')
    new_sentence = ''
    for index_word, word in enumerate(words, 1):
        new_sentence += word + ' '
        if index_word % max_words_per_line == 0:
            new_sentence += '\n'        
    return new_sentence.strip()


def run(filename: str):

    from robots.rw_robot.robot import read_file, write_file
    import os   

    # Import search content
    try:
        search_content = read_file(filename=filename)
    except Exception as e:
        raise e

    #--------------------------------------------------------------------------------
    # Creates video content
    video_content = {
        'images': [], 
        'sentences': [], 
        'duration_images': [], 
        'duration_sentences': [],
        'start_sentences_in': [],
        'font_size': [],
        'text_position': []
    }

    words_per_min = 150
    words_per_line = 10
    viewing_time = 3

    must_have = (
        search_content['items'],
        search_content['project_folder']
    )
    if all(must_have):
        items = search_content['items'].copy()
        # Create front cover
        cover = {
            'sentence': search_content['search_term'],
            'keywords': search_content['search_term'],
            'downloaded_image': 'cover.jpg',
        }        
        items.insert(0, cover)
        # Create back cover
        cover = {
            'sentence': {'en': 'The End', 'pt': 'Fim'}.get(search_content['search_lang']),
            'keywords': search_content['search_term'],
            'downloaded_image': 'cover.jpg',
        }        
        items.append(cover)       

        import json
        with open('video_content.json', 'w+') as file_handle:
            file_handle.write(json.dumps(items, indent=2))

        for item in items:
            must_have = (
                item.get('sentence'),
                item.get('downloaded_image')
            )
            if all(must_have):
                img_path = os.path.join(
                    search_content['project_folder'], 
                    'video_images',
                    item['downloaded_image']
                )
                
                # Calculating the amount of time needed to read each sentence
                number_words = len(item['sentence'].split(' '))
                t_sentence = round(60 * (number_words / words_per_min), 1) # time in seconds

                if os.path.split(img_path)[1] == 'cover.jpg':
                    video_content['sentences'].append(insert_breaklines(item['sentence'], words_per_line).title())
                    video_content['duration_sentences'].append(3)                    
                    video_content['start_sentences_in'].append(viewing_time/2 + sum(video_content['duration_images']))                
                    video_content['images'].append(img_path)
                    video_content['duration_images'].append(5)                              
                    video_content['font_size'].append(150)
                    video_content['text_position'].append('center')                                       
                else:
                    video_content['sentences'].append(insert_breaklines(item['sentence'], words_per_line))
                    video_content['duration_sentences'].append(t_sentence)
                    video_content['start_sentences_in'].append(viewing_time/2 + sum(video_content['duration_images']))                
                    video_content['images'].append(img_path)
                    video_content['duration_images'].append(round(t_sentence + viewing_time, 1))
                    video_content['font_size'].append(30)
                    video_content['text_position'].append('bottom')
    
        search_content['video_content'] = video_content

        # Save data structure
        write_file(
            filename=filename,
            content=search_content
        )
    #--------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------
    # Renderizing video
    if search_content['video_content']:
        create_video(
            video_content=search_content['video_content'], 
            dst_path=search_content['project_folder']
        )
    #--------------------------------------------------------------------------------