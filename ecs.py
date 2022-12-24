import boto3
session = boto3.Session(profile_name='default')
client = session.client('ecs')
paginator = client.get_paginator('list_clusters')
response_iterator = paginator.paginate()
l = []
def aws_service_ecs():
    for clusters_arn in response_iterator:
        for each_cluster_arn in clusters_arn['clusterArns']:
            tags_inside_cluster = client.list_tags_for_resource(
            resourceArn=each_cluster_arn
            )  
            cluster_tag = tags_inside_cluster['tags']
            result_of_the_tag = next(
               ((item for item in cluster_tag if item['key']=='Channel')),
               {}
            )
            result_of_next_tag = next(
               ((item for item in cluster_tag if item ['key']=='Env')),
               {}
            )
            task_list = client.list_tasks(
               cluster = (each_cluster_arn)
            )
            task_arn_inside_task_list =(task_list['taskArns'])
            for elements_in_task_list in task_arn_inside_task_list:
                task_arn = (elements_in_task_list)
                task_name = (elements_in_task_list.split('/')[1])
                task_id = (elements_in_task_list.split ('/')[2]) 
                
                describe_task =  client.describe_tasks(
                cluster = (each_cluster_arn),
                tasks =[
                 task_id
                 ]
                )
                containers = []
                tasks = describe_task['tasks']

                for task_details in tasks:
                    containers = task_details['containers']
                    task_definition_name  = task_details['taskDefinitionArn']
                    for container in containers:
                                            
                        str = (f"ClusterName = {each_cluster_arn.split('/')[1]}")
                        dictionary = dict(subString.split("=") for subString in str.split(";"))
                        
                        #Task id or Name

                        str1 = (f"TaskId/Name = {task_name}")
                        dictionary1 = dict(subString.split("=") for subString in str1.split(";"))
                    
                        #Task Def id or name
                        str2 = (f"TaskDefId/Name = {task_definition_name.split('/')[1]}")   
                        dictionary2 = dict(subString.split("=") for subString in str2.split(";"))
                    
                        #Image name
                        image = (container['name'])
                        str3 = (f"ImageName = {image}")
                        dictionary3 = dict(subString.split("=") for subString in str3.split(";"))
                        
                        #Image tag
                        image_tag = (container['image'])
                        str4 = (f"ImageTag = {image_tag}")
                        dictionary4 = dict(subString.split("=") for subString in str4.split(";"))
                    
                        #Tag of channel
                        str5 = (f"ValueOfClusterTag_Channel = {result_of_the_tag.get('value')}")
                        dictionary5 = dict(subString.split("=") for subString in str5.split(";"))
                    
                        #Tag for Env
                        str6 = (f"ValueOfClusterTag_Env = {result_of_next_tag .get('value')}")
                        dictionary6 = dict(subString.split("=") for subString in str6.split(";"))
                        
                        def Merge (dictionary,dictionary1,dictionary2,dictionary3,dictionary4,dictionary5,dictionary6):
                            res = dictionary|dictionary1 | dictionary2 | dictionary3 |dictionary4 |dictionary5|dictionary6
                            return res 

                        merge_of_whole_dict = Merge(dictionary,dictionary1, dictionary2 , dictionary3 ,dictionary4 ,dictionary5,dictionary6)    
                                                
                        dict_copy = merge_of_whole_dict.copy()
                        l.append(dict_copy)
                    
aws_service_ecs()

#Csv File 
import csv
my_list_of_dicts = l

#field names /names
names_present_inside_listOFdicts = ['ClusterName ','TaskId/Name ', 'TaskDefId/Name ', 'ImageName ', 'ImageTag ', 'ValueOfClusterTag_Channel ','ValueOfClusterTag_Env ']

#name of the csv file 
filename = 'Ecs_report.csv'   

#Writing csv file 
with open (filename, 'w') as csvfile:
    writer = csv.DictWriter(csvfile,fieldnames =names_present_inside_listOFdicts )    
    
    writer.writeheader()          
    writer.writerows(my_list_of_dicts)

 


                                
                            

                    

                    

                    
