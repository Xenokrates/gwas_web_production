from flask import Flask,  request,jsonify, render_template, redirect, url_for, send_file, Markup, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email
from modules import run_lmm
from flask import render_template

from flask_uploads import configure_uploads, UploadSet, TEXT
# https://getbootstrap.com/docs/4.0/components/modal/
import plot_layout

app = Flask(__name__)

# Flask-WTF requires an enryption key - the string can be anything
app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'
app.config['UPLOADED_TEXT_DEST'] = 'data/uploads'

# File upload configuration
files_to_upload = UploadSet('text', TEXT)
configure_uploads(app, files_to_upload)

# Flask-Bootstrap requires this line
Bootstrap(app)

# -math.log10(0.05 / len(pvals))
@app.route('/run_gwas',methods=['POST'])
def run_gwas(geno, pheno):
    if geno == "Barley WGS":
        geno_file = "barley/wgs_200cc_0025_003"
    if pheno == "BGT_96hai":
        pheno_file = "barley/bgt_bin_blues.txt"
    else:
        pheno_file = pheno
    # fast-lmm requires the fam file in a specific way and chromosomes should be labeled with ints (but not 0)
    results_df = run_lmm(geno_file, pheno_file)
    results_df.to_csv("data/results/out.csv")
    #return results_df


# Flask-WTF forms
class NameForm(FlaskForm):
    name = StringField('Email Adress', validators=[DataRequired()], default='luecks@gmail.com')
    geno_file = SelectField("Species", choices=['Barley WGS'])
    pheno_file = SelectField('Choose Phenotype', choices=['None', 'BGT_96hai'])
    pheno_upload = FileField('Upload Phenotype')

    ids_file = SelectField('Choose Core collection', choices=['None', '200cc'])
    id_upload = FileField('Upload ID List')
    #kinship_file = StringField('Upload Kinship matrix', render_kw={"placeholder": "optional"})
    kinship_upload = FileField('Upload Kinship matrix')
    #kinship_upload = FileField(' ')

    submit = SubmitField('Submit')


# all Flask routes below
@app.route('/', methods=['GET', 'POST'])
def index():
    names = ['luecks@gmail.com']
    form = NameForm()

    message = ""

    if form.validate_on_submit():
        name = form.name.data
        #pheno = form.pheno_file.data
        geno = form.geno_file.data
        if form.pheno_upload.data:
            pheno = files_to_upload.save(form.pheno_upload.data)
            pheno = "uploads/" + pheno
        else:
            pheno = form.pheno_file.data

        if pheno == "None" or pheno is None:
            message = "Please upload a phenotype file or choose a phenotype."
        else:
            message = ""
            run_gwas(geno, pheno)
            plot_layout.start_plotting('data/results/out.csv')
            message = "Anaylsis done, please check your Email."
        #print (pheno)
        #flash('Looks like you have changed your name!')


        #plot_layout.start_plotting('out.csv')


        #print (form.pheno_upload.data)
        #filename = files_to_upload.save(form.pheno_upload.data)
        #print (filename)


        #f = form.pheno_upload.file
        #filename = secure_filename(f.filename)
        #wgs_200cc_0025_003
        #print (name, pheno, geno, f, filename)
        #run(geno, pheno)
        #redirect("plot_bok.html")

        #if name.lower() in names:
            # empty the form field
            #form.name.data = ""
            #hello()
            #id = get_id(ACTORS, name)
            # redirect the browser to another route and template
            #return redirect( url_for('actor', id=id) )
            #results_df = run(geno, pheno)

            #plot()
            #return render_template('plot_bok.html')

            #return redirect("< a href =”plot_bok.html” target =”_blank” > my awesome link < / a >")


            # results_df = run(geno, pheno)
            #
            # bytes_obj = get_plot_as_bytes(results_df)
            # return send_file(bytes_obj,
            #                  attachment_filename='plot.png',
            #                  mimetype='image/png')
            #return redirect("plot_bok")
            # plots = []
            # plots.append(make_plot())
            #
            # return render_template('dashboard.html', plots=plots)

        #else:
            #message = "That actor is not in our database."
    return render_template('index.html', names=names, form=form, message=message)


@app.route('/gwas', methods=['GET', 'POST'])
def gwas():

    data = request.get_json(force=True)
    return jsonify(data)
    #prediction = model.predict([np.array(list(data.values()))])

    #output = prediction[0]
    #return jsonify(output)

# 2 routes to handle errors - they have templates too
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# keep this as is
if __name__ == '__main__':
    app.run(debug=True)