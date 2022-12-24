import boto3
from moto import mock_ecs
from moto import mock_ecs, mock_ec2
from moto.ec2 import utils as ec2_utils
import json 
from datetime import datetime
mock_ec2,mock_ecs
ACCOUNT_ID = 123456789012
ImageId='ami-12c6146b'
client = boto3.client("ecs", region_name="us-east-1")

def test_create_cluster():
    response = client.create_cluster(clusterName="dev")
    response["cluster"]["clusterArn"]==(
        f"arn:aws:ecs:us-east-1:ami-12c6146b:cluster/dev"
    )
    #print(response)
#test_create_cluster()    
#List clusters

def test_list_clusters():
    response = client.list_clusters()
    response["clusterArns"]==(
        f"arn:aws:ecs:us-east-2:{ACCOUNT_ID}:cluster/dev"
    )
    #print(response)
#test_list_clusters()    
#-----------------------

@mock_ec2
@mock_ecs
def test_run_task():
    client = boto3.client("ecs", region_name="us-east-1")
    ec2 = boto3.resource("ec2", region_name="us-east-1")

    test_cluster_name = "test_ecs_cluster"

    _ = client.create_cluster(clusterName=test_cluster_name)

    test_instance = ec2.create_instances(
        ImageId='ami-12c6146b', MinCount=1, MaxCount=1
    )[0]

    instance_id_document = json.dumps(
        ec2_utils.generate_instance_identity_document(test_instance)
    )

    response = client.register_container_instance(
        cluster=test_cluster_name, instanceIdentityDocument=instance_id_document
    )
   
    _ = client.register_task_definition(
        family="test_ecs_task",
        containerDefinitions=[
            {
                "name": "hello_world",
                "image": "docker/hello-world:latest",
                "cpu": 1024,
                "memory": 400,
                "essential": True,
                "environment": [
                    {"name": "AWS_ACCESS_KEY_ID", "value": "SOME_ACCESS_KEY"}
                ],
                "logConfiguration": {"logDriver": "json-file"},
            }
        ],
    )
    response = client.run_task(
        cluster="test_ecs_cluster",
        overrides={},
        taskDefinition="test_ecs_task",
        startedBy="moto",
    )
    len(response["tasks"])==(1)
    response = client.run_task(
        cluster="test_ecs_cluster",
        overrides={},
        taskDefinition="test_ecs_task",
        count=2,
        startedBy="moto",
        tags=[
            {"key": "tagKey0", "value": "tagValue0"},
            {"key": "tagKey1", "value": "tagValue1"},
        ],
    )
    len(response["tasks"])==(2)
    response["tasks"][0]["taskArn"]==(
        f"arn:aws:ecs:us-east-1:{ACCOUNT_ID}:task/"
    )
    response["tasks"][0]["clusterArn"]==(
        f"arn:aws:ecs:us-east-1:{ACCOUNT_ID}:cluster/test_ecs_cluster"
    )
    response["tasks"][0]["taskDefinitionArn"]==(
        f"arn:aws:ecs:us-east-1:{ACCOUNT_ID}:task-definition/test_ecs_task:1"
    )
    response["tasks"][0]["containerInstanceArn"]==(
        f"arn:aws:ecs:us-east-1:{ACCOUNT_ID}:container-instance/"
    )
  
test_run_task() 
#------------------

@mock_ec2
@mock_ecs
def test_list_tasks():
    client = boto3.client("ecs", region_name="us-east-1")
    ec2 = boto3.resource("ec2", region_name="us-east-1")

    _ = client.create_cluster()

    test_instance = ec2.create_instances(
        ImageId='ami-12c6146b', MinCount=1, MaxCount=1
    )[0]

    instance_id_document = json.dumps(
        ec2_utils.generate_instance_identity_document(test_instance)
    )

    _ = client.register_container_instance(
        instanceIdentityDocument=instance_id_document
    )

    container_instances = client.list_container_instances()
    container_instance_id = container_instances["containerInstanceArns"][0].split("/")[
        -1
    ]

    _ = client.register_task_definition(
        family="test_ecs_task",
        containerDefinitions=[
            {
                "name": "hello_world",
                "image": "docker/hello-world:latest",
                "cpu": 1024,
                "memory": 400,
                "essential": True,
                "environment": [
                    {"name": "AWS_ACCESS_KEY_ID", "value": "SOME_ACCESS_KEY"}
                ],
                "logConfiguration": {"logDriver": "json-file"},
            }
        ],
    )

    _ = client.start_task(
        taskDefinition="test_ecs_task",
        overrides={},
        containerInstances=[container_instance_id],
        startedBy="foo",
    )

    _ = client.start_task(
        taskDefinition="test_ecs_task",
        overrides={},
        containerInstances=[container_instance_id],
        startedBy="bar",
    )

    assert len(client.list_tasks()["taskArns"])==(2)
    assert len(client.list_tasks(startedBy="foo")["taskArns"])==(1)
#--------------------------------


@mock_ec2
@mock_ecs
def test_describe_tasks():
    client = boto3.client("ecs", region_name="us-east-1")
    ec2 = boto3.resource("ec2", region_name="us-east-1")

    test_cluster_name = "test_ecs_cluster"

    _ = client.create_cluster(clusterName=test_cluster_name)

    test_instance = ec2.create_instances(
        ImageId='ami-12c6146b', MinCount=1, MaxCount=1
    )[0]

    instance_id_document = json.dumps(
        ec2_utils.generate_instance_identity_document(test_instance)
    )

    client.register_container_instance(
        cluster=test_cluster_name, instanceIdentityDocument=instance_id_document
    )

    _ = client.register_task_definition(
        family="test_ecs_task",
        containerDefinitions=[
            {
                "name": "hello_world",
                "image": "docker/hello-world:latest",
                "cpu": 1024,
                "memory": 400,
                "essential": True,
                "environment": [
                    {"name": "AWS_ACCESS_KEY_ID", "value": "SOME_ACCESS_KEY"}
                ],
                "logConfiguration": {"logDriver": "json-file"},
            }
        ],
    )
    tasks_arns = [
        task["taskArn"]
        for task in client.run_task(
            cluster="test_ecs_cluster",
            overrides={},
            taskDefinition="test_ecs_task",
            count=2,
            startedBy="moto",
        )["tasks"]
    ]
    response = client.describe_tasks(cluster="test_ecs_cluster", tasks=tasks_arns)

    len(response["tasks"])==(2)
    set(
        [response["tasks"][0]["taskArn"], response["tasks"][1]["taskArn"]]
    )==(set(tasks_arns))

    # Test we can pass task ids instead of ARNs
    response = client.describe_tasks(
        cluster="test_ecs_cluster", tasks=[tasks_arns[0].split("/")[-1]]
    )
    len(response["tasks"])==(1)


        


test_create_cluster()    
test_list_clusters()
test_run_task()
test_list_tasks()
test_describe_tasks()
