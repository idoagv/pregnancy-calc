import os
from datetime import date, datetime

from flask import (
    Flask,
    flash,
    get_flashed_messages,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)

from calc import edd_from_lmp, lmp_from_gestational_age, screening_windows, status
from i18n import TRANSLATIONS, get_translator
from models import Patient, db

DEFAULT_LANG = "he"


def create_app(db_path: str | None = None) -> Flask:
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    db_path = db_path or os.environ.get(
        "CALC_DB_PATH", os.path.join(os.path.dirname(__file__), "calc.db")
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.context_processor
    def inject_i18n():
        lang = request.cookies.get("lang", DEFAULT_LANG)
        if lang not in TRANSLATIONS:
            lang = DEFAULT_LANG
        return {
            "t": get_translator(lang),
            "lang": lang,
            "dir": "rtl" if lang == "he" else "ltr",
            "other_lang": "en" if lang == "he" else "he",
        }

    @app.route("/")
    def index():
        result = None
        form = {
            "mode": request.args.get("mode", "lmp"),
            "lmp": request.args.get("lmp", ""),
            "cycle": request.args.get("cycle", "28"),
            "as_of": request.args.get("as_of", date.today().isoformat()),
            "weeks": request.args.get("weeks", ""),
            "days": request.args.get("days", "0"),
        }
        error = None
        if request.args.get("calc"):
            try:
                cycle = int(form["cycle"] or 28)
                if form["mode"] == "lmp" and form["lmp"]:
                    lmp = date.fromisoformat(form["lmp"])
                elif form["mode"] == "age" and form["weeks"]:
                    on_date = date.fromisoformat(
                        form["as_of"] or date.today().isoformat()
                    )
                    lmp = lmp_from_gestational_age(
                        int(form["weeks"]), int(form["days"] or 0), on_date, cycle
                    )
                else:
                    lmp = None
                if lmp is not None:
                    today = date.today()
                    s = status(lmp, today, cycle)
                    result = {
                        "lmp": lmp,
                        "edd": s.edd,
                        "weeks": s.weeks,
                        "days": s.days,
                        "trimester": s.trimester,
                        "days_remaining": s.days_remaining,
                        "screenings": screening_windows(lmp, today),
                    }
            except (ValueError, TypeError) as e:
                error = str(e)
        return render_template(
            "index.html", form=form, result=result, error=error,
            messages=get_flashed_messages(),
        )

    @app.route("/save", methods=["POST"])
    def save():
        name = (request.form.get("name") or "").strip()
        phone = (request.form.get("phone") or "").strip()
        lmp_s = request.form.get("lmp") or ""
        edd_s = request.form.get("edd") or ""
        notes = (request.form.get("notes") or "").strip() or None

        lang = request.cookies.get("lang", DEFAULT_LANG)
        t = get_translator(lang)

        if not name:
            flash(t("error_name"))
            return redirect(url_for("index"))
        if not phone:
            flash(t("error_phone"))
            return redirect(url_for("index"))

        patient = Patient(
            name=name,
            phone=phone,
            lmp=date.fromisoformat(lmp_s) if lmp_s else None,
            edd=date.fromisoformat(edd_s) if edd_s else None,
            notes=notes,
        )
        db.session.add(patient)
        db.session.commit()
        flash(t("saved_ok"))
        return redirect(url_for("index"))

    @app.route("/patients")
    def patients():
        rows = Patient.query.order_by(Patient.created_at.desc()).all()
        return render_template("patients.html", patients=rows)

    @app.route("/lang/<code>")
    def set_lang(code: str):
        if code not in TRANSLATIONS:
            code = DEFAULT_LANG
        resp = make_response(redirect(request.referrer or url_for("index")))
        resp.set_cookie("lang", code, max_age=60 * 60 * 24 * 365)
        return resp

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
