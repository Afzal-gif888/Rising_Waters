from flask import Blueprint, render_template, request

from ..services.prediction_service import predict_flood

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("home.html")


@main.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        form_data = request.form.to_dict()
        try:
            prediction = predict_flood(form_data)
        except (ValueError, FileNotFoundError, RuntimeError) as exc:
            return render_template("predict.html", error=str(exc), inputs=form_data)

        return render_template("result.html", prediction=prediction, inputs=form_data)

    return render_template("predict.html", error=None, inputs={})


