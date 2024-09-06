resource "aws_ebs_volume" "chrome_profiles_store" {
    availability_zone = "us-east-1a"
    size              = 200         # Size in GB
    type              = "sc1"        # Cold HDD
    tags = {
        Name = "ChromeProfilesStore"
    }
}