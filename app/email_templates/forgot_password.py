from enum import Enum

class ForgotPasswordEnum(Enum):
    """Enum for Forgot Password types"""
    email_template = """
                <div style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
                    <h1 style="color: #4CAF50;">Password Reset Request</h1>
                    <p>Hello <strong>{first_name}</strong>,</p>
                    <p>We received a request to reset your password. If you didn't make the request, just ignore this email. Otherwise, you can reset your password using this link:</p>
                    <a href="{command_center_link}resetpassword?email={receiver_email}&uid={unique_id}" style="background-color: #4CAF50; border: none; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 20px 0; cursor: pointer; border-radius: 5px;">Reset Password</a>
                    <p>If you didn't request this, please ignore this email.</p>
                    <p style="margin-top: 50px;">Best,</p>
                    <p><strong>Eventonaut Team</strong></p>
                </div>
                """

    @classmethod
    def email(cls, first_name, command_center_link, receiver_email, unique_id):
        return cls.email_template.value.format(first_name=first_name, command_center_link=command_center_link, receiver_email=receiver_email, unique_id=unique_id)