"""Paymob Payment Gateway Configuration"""

class PaymobConfig:
    """Paymob gateway settings"""
    
    # API Configuration
    API_KEY = "ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiR0F6Y3lJNklrMWxjbU5vWVc1MElpd2ljSEp2Wm1sc1pWOXdheUk2T1RnNE5EWXpMQ0p1WVcxbElqb2lNVGN5TXpFd09UQTFPUzQyTlRFd09EWWlmUS5tdFNMa05GNnBxTTVmMVF5T0RiS0xiR21kb1FwOUZHZS1QcjdTVXhJbVp0N1htOWhnLThLNWdMN1BCSEJ0TXl5SUJnUlUwTm9fWF9vWGFOUF9INmFXUQ=="
    
    # Integration IDs
    CARD_INTEGRATION_ID = 4623557
    MOBILE_WALLET_INTEGRATION_ID = 4626585
    
    # iFrame ID for card payments only
    CARD_IFRAME_ID = 859704
    
    # Security
    HMAC_SECRET = "14B6ABDF04E5BF1E6F1FB55A42CCFB86"
    
    # URLs
    BASE_URL = "https://accept.paymob.com/api"
    
    # Endpoints
    AUTH_URL = f"{BASE_URL}/auth/tokens"
    ORDER_URL = f"{BASE_URL}/ecommerce/orders"
    PAYMENT_KEY_URL = f"{BASE_URL}/acceptance/payment_keys"
    
    # iFrame URL (for backward compatibility)
    IFRAME_ID = CARD_IFRAME_ID
    IFRAME_URL = f"https://accept.paymob.com/api/acceptance/iframes/{CARD_IFRAME_ID}"
    
    # Currency
    CURRENCY = "EGP"
    
    # Test Mode flags
    TEST_MODE = False
    DEMO_MODE = False
    
    @staticmethod
    def get_iframe_url(payment_token):
        """Generate iFrame URL for card payments"""
        return f"https://accept.paymob.com/api/acceptance/iframes/{PaymobConfig.CARD_IFRAME_ID}?payment_token={payment_token}"
    
    @staticmethod
    def get_mobile_wallet_url(payment_token):
        """Generate redirect URL for mobile wallet payments"""
        return f"https://accept.paymob.com/api/acceptance/post_pay?token={payment_token}"
