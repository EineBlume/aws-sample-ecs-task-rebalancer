## Intro
AWS-ECS 작업 리발란서 예시 프로젝트입니다.

## Quick start

1. Run `pip install -r requirements.txt`<br />
2. Update `config.yaml`
3. Run `lambda deploy`

## Guide

1. 배포툴로 [python-lambda](https://github.com/nficano/python-lambda) 라이브러리를 사용하고 있습니다.<br/>
   * *deploy_s3 커맨드에 버그가 있다. - 2018년 1월 24일까지 존재함.*
2. `Bot`을 스케줄링하여 사용하고 싶다면 [링크](https://docs.aws.amazon.com/ko_kr/AmazonCloudWatch/latest/events/RunLambdaSchedule.html)를 참고


## Role
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
                "sqs:SendMessage",
                "sns:ListSubscriptions",
                "sqs:GetQueueUrl",
                "sns:Publish"
            ]
        }
    ]
}
```

## Invoke

1. `event.json`을 활용하여 로컬에서 테스트할 수 있습니다.
2. `lambda invoke -v` 명령어로 로컬에서 테스트할 수 있습니다.


## Deploy

`lambda deploy` 명령어를 통해 배포할 수 있습니다(실행하면 `AWS-Lambda` 함수를 만듬). 


