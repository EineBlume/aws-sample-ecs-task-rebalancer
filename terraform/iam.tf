resource "aws_iam_policy" "ecs_task_rebalancer_asg_lifecycle_policy" {
  name = "ECSTaskRebalancerAutoScalingGroupLifecyclePolicy"

  policy = <<EOF
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
EOF
}

resource "aws_iam_policy" "ecs_task_rebalancer_lambda_excution_policy" {
  name = "ECSTaskRebalancerLambdaExcutionPolicy"
  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "autoscaling:CompleteLifecycleAction",
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "ec2:DescribeInstances",
                "ec2:DescribeInstanceAttribute",
                "ec2:DescribeInstanceStatus",
                "ec2:DescribeHosts",
                "ecs:ListContainerInstances",
                "ecs:SubmitContainerStateChange",
                "ecs:SubmitTaskStateChange",
                "ecs:DescribeContainerInstances",
                "ecs:UpdateContainerInstancesState",
                "ecs:ListTasks",
                "ecs:DescribeTasks",
                "sns:Publish",
                "sns:ListSubscriptions"
            ],
            "Resource": "*"
        }
    ]
}
EOF
}


resource "aws_iam_role" "ecs_lambda_execute_role_for_task_rebalance" {
  name = "ECS-LambdaExecuteRoleForTaskRebalance"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "ecs_lambda_excution_role_rebalance" {
  role = "${aws_iam_role.ecs_lambda_execute_role_for_task_rebalance.name}"
  policy_arn = "${aws_iam_policy.ecs_task_rebalancer_lambda_excution_policy.arn}"
}
