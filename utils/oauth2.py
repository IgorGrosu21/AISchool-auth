import aiohttp

from core import GOOGLE_CLIENT_ID, FACEBOOK_CLIENT_ID
from schemas import BadRequest

url_mapping = {
    "google": "https://oauth2.googleapis.com/tokeninfo?id_token={token}",
    "facebook": "https://graph.facebook.com/debug_token?input_token={token}&access_token={client_id}",
}

def validate_google_token(token_info: dict, email: str) -> dict:
    email_ok = "email" in token_info and token_info["email"].lower().strip() == email
    aud_ok = token_info["aud"] == GOOGLE_CLIENT_ID and token_info["azp"] == GOOGLE_CLIENT_ID
    email_verified_ok = token_info["email_verified"] == "true"

    if email_ok and aud_ok and email_verified_ok:
        return token_info

    raise BadRequest.exception(detail="invalid_oauth2_token", attr="token")

def validate_facebook_token(token_info: dict) -> dict:
    app_id_ok = token_info["app_id"] == FACEBOOK_CLIENT_ID.split("|")[0]
    type_ok = token_info["type"] == "USER"
    is_valid_ok = token_info["is_valid"]
    scopes_ok = "email" in token_info["scopes"] and "public_profile" in token_info["scopes"]

    if app_id_ok and type_ok and is_valid_ok and scopes_ok:
        return token_info

    raise BadRequest.exception(detail="invalid_oauth2_token", attr="token")

async def validate_oauth2_token(provider: str, token: str, email: str) -> str:
    if provider == "google":
        url = url_mapping["google"].format(token=token)
    elif provider == "facebook":
        url = url_mapping["facebook"].format(token=token, client_id=FACEBOOK_CLIENT_ID)
    else:
        raise BadRequest.exception(detail="invalid_oauth2_provider", attr="provider")

    try:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(url) as resp:
                    token_info = await resp.json()

                    if provider == "google":
                        validate_google_token(token_info, email)
                    elif provider == "facebook":
                        validate_facebook_token(token_info['data'])

                    return email
    except aiohttp.ClientResponseError as e:
        raise BadRequest.exception(detail="failed_to_validate_oauth2_token", attr="token") from e
    except BadRequest.exception:
        raise
    except Exception as e:
        raise BadRequest.exception(detail="invalid_oauth2_token", attr="token") from e