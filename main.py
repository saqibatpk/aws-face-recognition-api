import pprint
import json
import boto3
import os
import shutil

SIMILARITY_THRESHOLD = 75.0


def compare_images(client, source, target):
	with open(source, 'rb') as source_image:
		source_bytes = source_image.read()

	with open(target, 'rb') as target_image:
		target_bytes = target_image.read()

	response = client.compare_faces(
					SourceImage={ 'Bytes': source_bytes },
					TargetImage={ 'Bytes': target_bytes },
					SimilarityThreshold=SIMILARITY_THRESHOLD
	)
	return response


def create_collection(client, collection_id):
	response = client.create_collection(CollectionId = collection_id)
	return response


def add_face_to_collection(client, source, collection_id, external_image_id):
	with open(source, 'rb') as source_image:
		source_bytes = source_image.read()

	response = client.index_faces(
					CollectionId = collection_id,
					Image = {'Bytes': source_bytes},
					ExternalImageId = external_image_id
	)
	return response


def print_response(response):
	for face in response["FaceMatches"]:
		print("Image")
		print(face["Face"]["FaceId"])
		print(face["Face"]["ExternalImageId"])
		print("=====")

if __name__ == '__main__':

	#credentials entered through awscli using `aws configure`
	client = boto3.client('rekognition') 

	# COMPARING 2 IMAGES
	response = compare_images(client, "source.jpg","target.jpg")
	pprint.pprint(response)

	# CREATE A NEW COLLECTION
	collection_id = "test"
	response = create_collection(client, collection_id)
	pprint.pprint(response)

	# ADD A FACE TO A COLLECTION
	source = "source.jpg"
	collection_id = "test"
	external_image_id = "source.jpg"
	response = add_face_to_collection(client, source, collection_id, external_image_id)
	pprint.pprint(response)

	#SEARCH IN COLLECTION USING IMAGE
	source = "test_image.jpg"
	with open(source, 'rb') as source_image:
		source_bytes = source_image.read()
	response = client.search_faces_by_image(
		CollectionId = "test",
		Image = {'Bytes' : source_bytes}
	)
	pprint.pprint(response)

	#SEARCH USING FACE ID
	response = client.search_faces(
					CollectionId='test',
					FaceId='ef75efa7-724b-5e07-859e-7c0b0c476b9b', #face id
	)
	pprint.pprint(response)

	#PRINT FOUND FACES
	print_response(response)
	
	#ADD FOLDER TO COLLECTION
	foldername = "test"
	for filename in os.listdir(foldername):
		source = folder + "/" + filename
		collection_id = foldername
		external_image_id = foldername + "_" + filename
		response = add_face_to_collection(client, source, collection_id, external_image_id)
		print(filename + " : Added")


	#iterate over files in Test
	for filename in os.listdir("test"):

		#check if file is jpg
		if(filename.lower().endswith(".jpg")):
		
			#create folder with name as filename
			foldername = filename[:-4]
			os.makedirs("Result/"+foldername)

			#get source file in bytes
			source = "test/"+filename
			with open(source, 'rb') as source_image:
				source_bytes = source_image.read()
			
			#call api
			response = client.search_faces_by_image(
				CollectionId = "test",
				Image = {'Bytes' : source_bytes}
			)
			
			#for all matches move photo to folder
			for face in response["FaceMatches"]:
				print(face["Face"]["ExternalImageId"])
				file = face["Face"]["ExternalImageId"][len("test_"):]
				shutil.copyfile("test/"+file,"Result/"+foldername+"/"+file)

