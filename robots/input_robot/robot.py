def input_user() -> dict:

    input_user_dict = {}
   
    # Choosing the search laguange
    print('Choose one of the search languages below:')
    print('[1] English')
    print('[2] Portuguese')
    while True:
        ans = input()
        if ans in ('1','2'):
            input_user_dict['search_lang'] = {'1': 'en', '2': 'pt'}.get(ans)
            break
        else:
            print('Option not available!')
   
    # Choosing the search term
    print('Enter a search term: ')
    while True:
        ans = input()
        if ans:
            input_user_dict['search_term'] = ans
            break
        else:
            print('Enter something!')        

    # First proccess concluded
    input_user_dict['last_proccess'] = 'The user entered the search term and language.'

    return input_user_dict

def run() -> str:

    import os, datetime, json
    from robots.rw_robot.robot import write_file

    search_content = {}  

    # Request user
    search_content.update(input_user())
    
    # Ask for confirmation
    print(f"The search language is {search_content['search_lang']} and the search term is {search_content['search_term']}")
    print('Can I proceed?')
    print('[1] Yes')
    print('[2] No')
    print('[3] Exit')
    
    while True:
        ans = input()
        if ans == '1':
            # Create a project folder            
            folder_name = search_content['search_term'].replace(' ','_') + '_' + str(datetime.datetime.today()).split('.')[0].replace(' ', '_')
            if not os.path.exists(folder_name):        
                os.mkdir(folder_name)                
            # Save data structure
            filename = os.path.abspath(os.path.join(folder_name, 'search_content.json'))
            search_content['project_folder'] = os.path.abspath(os.path.join(folder_name))
            write_file(
                filename=filename, 
                content=search_content
            )            
            return filename
        elif ans == '2':
            return run()
        elif ans == '3':
            return ''
        else:
            print('Invalid choice!')