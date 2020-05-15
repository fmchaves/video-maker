def get_url_images(key_term: str, search_term: str, search_lang: str, credentials: dict) -> list:

    import requests, json

    # Defines search parameters
    params = {
        'key': credentials['api_key'], 
        'cx': credentials['search_engine_id'],         
        'lr': 'lang_' + search_lang,
        'exactTerms': key_term,
        'searchType': 'image',
        'imgType': 'photo',
        'imgSize': 'huge',
        'safe': 'active',
        #'rights': 'cc_publicdomain',
        'num': 10,  
        'q': search_term
    }

    # Search images
    results = requests.get(credentials['url'], params=params).json()

    # Select images
    images = []
    context_link = []
    if results.get('items'):        
        for item in results.get('items'):
            if item.get('link').lower().endswith('.jpg') or item.get('link').lower().endswith('.jpeg'):
                images.append(item.get('link'))
                context_link.append(item.get('image').get('contextLink'))
        images = [{'img_link': img_link, 'img_context_link': img_context_link} for img_link, img_context_link in zip(images, context_link)]
    return images

def standardize_image(source_path: str, dest_path: str) -> bool:

    from PIL import Image, ImageFilter
    
    # Standard width and height
    img_width, img_height = 1920, 1080
    # Open the image
    try:
        img_original = Image.open(source_path)
    except:
        print(f'It was not possible to open the image: {source_path}')
        return False

    if img_original.width != img_width or img_original.height != img_height:    
        # Creating a background blur image from the original image
        img_background = img_original.filter(ImageFilter.GaussianBlur(20))
        # Resizing the background image
        img_background = img_background.resize((img_width, img_height))    
        # If one of the dimensions of the original image is larger than the standard
        # dimensions, the image will be scaled proportionally
        if img_original.height > img_height or img_original.width > img_width:
            img_original.thumbnail((img_width, img_height))
        # Find the middle coordinates and place the original image over the background
        x, y = int((img_background.width - img_original.width)/2), int((img_background.height - img_original.height)/2)
        img_background.paste(img_original, box=(x, y))
        # Save new image
        img_background.save(dest_path)
    else:        
        img_original.save(dest_path)
    
    return True

def run(filename: str):
    
    from robots.rw_robot.robot import read_file, write_file
    import os, shutil, datetime, requests, time, json
    from PIL import Image

    # Import search content
    try:
        search_content = read_file(filename=filename)
    except Exception as e:
        raise e

    # Load credentials.json
    file_path = os.path.join(os.path.dirname(os.path.abspath(__name__)), 'credentials.json')
    credentials = read_file(filename=file_path)

    #--------------------------------------------------------------------------------
    # Get images link
    must_have = (
        search_content.get('search_term'), 
        search_content.get('search_lang'),
        search_content.get('items')
    )
    if  all(must_have):
        visited_links_imgs, visited_keywords = [], []
        for index_item, item in enumerate(search_content['items']):
            status = round(100*index_item/len(search_content['items']))
            print(f'\rSearching images... {status}%', end='')                        
            for keyword in item['keywords']:
                if keyword.lower() not in visited_keywords:
                    visited_keywords.append(keyword.lower())
                    response = get_url_images(
                        key_term=search_content['search_term'],
                        search_term=search_content['search_term'] + ' ' + keyword,
                        search_lang=search_content['search_lang'],
                        credentials=credentials['google-search']              
                    )
                # Eliminate duplicate links
                images = []
                for img in response:
                    if img['img_link'] not in visited_links_imgs:
                        images.append(img)
                        visited_links_imgs.append(img['img_link'])
                item['images'] = images[:2] # Save only two images
        else:         
            print(f'\rSearching images... 100%')

        search_content['last_proccess'] = 'The image URL for the keywords has been saved.'

        # Save data structure
        write_file(
            filename=filename,
            content=search_content
        )
    #--------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------
    # Download Images
    must_have = (        
        search_content.get('items')
    )
    if search_content.get('items'):          
        folder_name = os.path.join(search_content['project_folder'], 'downloaded_images')
        temp_folder_name = os.path.join(search_content['project_folder'], 'temp')
        # Create the folder to store images
        if not os.path.exists(folder_name):                     
            os.mkdir(folder_name)

        # Create the folder to store temp images
        if not os.path.exists(temp_folder_name):                     
            os.mkdir(temp_folder_name)        
                
        # Download images
        for index_item, item in enumerate(search_content['items']):
            status = round(100*index_item/len(search_content['items']))
            print(f'\rDownloading images... {status}%', end='')
            if not item.get('images'):                
                continue
            images = [urls.get('img_link') for urls in item.get('images')]
            flag = 0
            if images:  
                while True:
                    for url in images:                    
                        try:                        
                            response = requests.get(url).content
                            time.sleep(3)
                            img_filename = os.path.join(temp_folder_name, 'img_' + str(index_item) + os.path.splitext(url)[1])
                            with open(img_filename, 'wb') as file_handle:
                                file_handle.write(response)
                            time.sleep(2)
                            Image.open(img_filename)
                        except:
                            continue
                        else:
                            img_filename = os.path.join(folder_name, 'img_' + str(index_item) + os.path.splitext(url)[1])                        
                            with open(img_filename, 'wb') as file_handle:
                                file_handle.write(response)                        
                            flag = 1
                            item['downloaded_image'] = os.path.split(img_filename)[1]
                            break                    
                    if flag:
                        break
            else:
                item['downloaded_image'] = ''
        else:
            print(f'\rDownloading images... 100%')
        
        # Remove temporary directory
        shutil.rmtree(temp_folder_name)

        search_content['last_proccess'] = 'The images have been downloaded.'

        # Save data structure
        write_file(
            filename=filename,
            content=search_content
        )
    #--------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------
    # Standardize Images
    must_have = (        
        search_content.get('items')
    )
    if search_content.get('items'):
        video_imgs_path = os.path.join(search_content['project_folder'], 'video_images')                
        download_imgs_path = folder_name = os.path.join(search_content['project_folder'], 'downloaded_images')
        # Remove video images folder
        if os.path.exists(video_imgs_path):
            shutil.rmtree(video_imgs_path)
        # Copy downloaded images to video images folder
        shutil.copytree(download_imgs_path, video_imgs_path)
        # Create a cover image and save it in video images folder        
        cover = Image.new('RGB', (1920, 1080))
        cover.save(os.path.join(video_imgs_path, 'cover.jpg'))
        time.sleep(2)

        for index_img, img in enumerate(os.listdir(video_imgs_path)):
            status = round(100*index_img/len(os.listdir(video_imgs_path)))
            print(f'\rStandardizing images...{status}%', end='')
            time.sleep(3)
            img_path = os.path.join(video_imgs_path, img)            
            standardize_image(img_path, img_path)
        else:
            print(f'\rStandardizing images...100%')

        search_content['last_proccess'] = 'The images were standardized.'
        
        # Save data structure
        write_file(
            filename=filename,
            content=search_content
        )

        time.sleep(5)
    #--------------------------------------------------------------------------------