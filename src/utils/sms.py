import requests
import logging
from typing import Type, List
from abc import ABC, abstractmethod

from fastapi import HTTPException, status

from src.config import setting

logger = logging.getLogger("machanic")


class SmsABC(ABC):

    @abstractmethod
    def send_to_all(self, phone_numbers: List[str], msg:str) -> None:
        pass

    @abstractmethod
    def send_to_one(self, phone_number:str, msg:str):
        pass


class HiSms(SmsABC):
    def send_to_all(self, phone_numbers: List[str], msg:str):
        """ OneToOne method accord to document """
        try:
            url = setting.SMS_ENDPOINT
            username = setting.SMS_USER
            password = setting.SMS_PASSWORD
            originator = setting.SMS_ORIGINATOR
            
            params = {
                "username": username,
                "password": password,
                "from": originator,
                "message": msg
            }

            results = []
            for phone_number in phone_numbers:
                params["to"] = phone_number
                response = requests.get(url, params=params)
                results.append(f"{phone_number} with status: {response}")
                
            loggs = ", ".join(results) + "sent."
            logger.info(loggs)

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail= f"Error at connecting to service panel."
            )
    
    def send_to_one(self, phone_number: str, msg:str):
        try:
            url = setting.SMS_ENDPOINT
            username = setting.SMS_USER
            password = setting.SMS_PASSWORD
            originator = setting.SMS_ORIGINATOR
            
            params = {
                "username": username,
                "password": password,
                "from": originator,
                "message": msg
            }


            params["to"] = phone_number
            response = requests.get(url, params=params)
            logger.info(f"{phone_number} result: {response.text} sent.")
                

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail= f"Error at connecting to service panel."
            )



class SmsPanelFactory:
    
    @staticmethod
    def get_sms_panel(sms_panel:str) -> Type[SmsABC]:
        pannels = {
            "hi_sms": HiSms,
        }
        
        Panel = pannels.get(sms_panel)
        if Panel is not None:
            return Panel() 
    
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Sms panel not implanted."
        )
    