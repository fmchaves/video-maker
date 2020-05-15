def read_file(filename: str):

	import json

	with open(filename, mode='r') as file_handle:
		content = file_handle.read()
	return json.loads(content, encoding='utf-8')

def write_file(filename: str, content: str):

	import json

	with open(filename, mode='w+') as file_handle:
		file_handle.write(json.dumps(obj=content, indent=2, ensure_ascii=False))
	
