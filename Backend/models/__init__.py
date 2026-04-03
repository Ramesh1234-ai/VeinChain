from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy
from .User_model import User
from .Request_model import BloodRequest
from .Donation_model import Donation
from .Notification_model import Notification
from .ContactMessage_model import ContactMessage
from .Donor_model import Donor

