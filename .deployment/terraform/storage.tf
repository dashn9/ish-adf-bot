# resource "aws_ebs_volume" "chrome_profiles_store" {
#     availability_zone = "us-east-1a"
#     size              = 400         # Size in GB
#     type              = "sc1"        # Cold HDD
#     tags = {
#         Name = "ChromeProfilesStore"
#     }
# }

resource "aws_iam_policy" "ebs_csi_policy" {
  name        = "AmazonEKS_EBS_CSI_Driver_Policy"
  description = "Policy for EBS CSI Driver"
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "ec2:CreateSnapshot",
          "ec2:AttachVolume",
          "ec2:DetachVolume",
          "ec2:ModifyVolume",
          "ec2:DeleteVolume",
          "ec2:DescribeAvailabilityZones",
          "ec2:DescribeInstances",
          "ec2:DescribeSnapshots",
          "ec2:DescribeTags",
          "ec2:DescribeVolumes",
          "ec2:CreateTags"
        ],
        "Resource": "*"
      }
    ]
  })
}


resource "aws_iam_role" "ebs_csi_role" {
  name = "ISH_BOT_EBS_CSI_DriverRole"

  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "eks.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_policy" {
  policy_arn = aws_iam_policy.ebs_csi_policy.arn
  role       = aws_iam_role.ebs_csi_role.name
}

resource "aws_iam_instance_profile" "ebs_csi_instance_profile" {
  name = "ISH_BOT_EBS_CSI_InstanceProfile"
  role = aws_iam_role.ebs_csi_role.name
}