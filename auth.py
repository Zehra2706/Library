from flask import flash, request, redirect, url_for
from functools import wraps
from flask import request, redirect, jsonify,  url_for
import jwt
from config import Config
from flask import g

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        def api_error(msg, code=401):
            return jsonify({"error": msg}), code

        is_api = request.path.startswith("/api/")

        token = request.cookies.get("token")

        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

       
        if not token:
            if is_api:
                return api_error("Token gerekli")

            resp = redirect(url_for("user_bp.index"))
            resp.set_cookie("token", "", expires=0)
            flash("Giriş yapmanız gerekiyor", "warning")
            return resp

        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])

            g.user_id = data.get("user_id")
            g.rol = str(data.get("rol", "")).strip().lower().replace("ı", "i")

            if g.rol not in ["kullanici", "personel"]:
                if is_api:
                    return api_error("Yetkisiz işlem")

                resp = redirect(url_for("user_bp.index"))
                resp.set_cookie("token", "", expires=0)
                flash("Yetkisiz işlem", "danger")
                return resp

        except jwt.ExpiredSignatureError:
            if is_api:
                return api_error("Token süresi doldu")

            resp = redirect(url_for("user_bp.index"))
            resp.set_cookie("token", "", expires=0)
            flash("Oturum süresi doldu", "warning")
            return resp

        except jwt.InvalidTokenError:
            if is_api:
                return api_error("Geçersiz token")

            resp = redirect(url_for("user_bp.index"))
            resp.set_cookie("token", "", expires=0)
            flash("Geçersiz oturum", "warning")
            return resp

        return f(*args, **kwargs)

    return decorated