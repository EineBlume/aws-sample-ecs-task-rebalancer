## Intro
AWS-ECS 클러스터 인스턴스가 `Scale-Out`될때 작업 재배치 해주는 예시 프로젝트입니다.


## Quick start

1. Run `pip install -r requirements.txt`<br />
2. Update `config.yaml`
3. Run `lambda deploy`
	* 배포툴로 [python-lambda](https://github.com/nficano/python-lambda) 라이브러리를 사용하고 있습니다.
4. SNS 주제를 만들고 배포된 람다 함수를 구독
5. ASG 시작 알람 생성 (웹 콘솔에서 가능)


## Invoke

1. `event.json`을 활용하여 로컬에서 테스트할 수 있습니다.
2. `lambda invoke -v` 명령어로 로컬에서 테스트할 수 있습니다.


## Deploy

`lambda deploy` 명령어를 통해 배포할 수 있습니다(실행하면 `AWS-Lambda` 함수를 만듬). 


## ASG Notification Policy
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Resource": "*",
            "Action": [
                "sqs:SendMessage",
                "sqs:GetQueueUrl",
                "sns:Publish"
            ]
        }
    ]
}
```

## Lambda Execute Policy
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "ec2:DescribeInstances",
                "ec2:DescribeInstanceAttribute",
                "ec2:DescribeInstanceStatus",
                "ec2:DescribeHosts",
                "ecs:ListContainerInstances",
                "ecs:DescribeContainerInstances",
                "ecs:ListTasks",
                "ecs:DescribeTasks",
                "ecs:listServices",
                "ecs:DescribeServices",
                "ecs:updateService"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Resource": "*",
            "Action": [
                "sns:ListSubscriptions",
                "sns:Publish"
            ]
        }
    ]
}
```

