import inspect
from flask import Flask, request
from flask_migrate import Migrate
import psycopg2
from sqlalchemy_serializer import SerializerMixin
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
import jsonify


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://api_db_n7hc_user:nfCmFcmTNNBX4Ryr2qllRychVlwTLRHA@dpg-cfurmohmbjsj9amd0hp0-a.oregon-postgres.render.com/api_db_n7hc"

# "postgresql://postgres:toor@localhost:5432/postgres"
# postgresql://api_db_n7hc_user:nfCmFcmTNNBX4Ryr2qllRychVlwTLRHA@dpg-cfurmohmbjsj9amd0hp0-a.oregon-postgres.render.com/api_db_n7hc
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

jsonData = {}

api = Api(app)
app.app_context().push()


class CountryModel(db.Model, SerializerMixin):
    serialize_rules = ('-neighbour', 'id',)
    # serialize_only = ('id',)
    __tablename__ = 'country'
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String,  nullable=False)
    cca3 = db.Column(db.String,  nullable=False)
    currency_code = db.Column(db.String,  nullable=False)
    currency = db.Column(db.String,  nullable=False)
    capital = db.Column(db.String,  nullable=False)
    region = db.Column(db.String,  nullable=False)
    subregion = db.Column(db.String,  nullable=False)
    area = db.Column(db.Text[100], nullable=False)
    map_url = db.Column(db.String,  nullable=False)
    population = db.Column(db.Text[100])
    flag_url = db.Column(db.String,  nullable=False)
    neighbour = db.relationship(
        'CountryNeighbour', backref='country', lazy='dynamic')


class CountryNeighbour(db.Model, SerializerMixin):
    serialize_rules = ('-neighbour_id', 'id',)
    __tablename__ = 'neighbour'
    id = db.Column(db.String, nullable=False, primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey(
        'country.id'), nullable=False)
    neighbour_id = db.Column(db.String,  nullable=False)
    created_at = db.Column(db.String,  nullable=False)
    updated_at = db.Column(db.String)


class add_country(Resource):
    def post(self):
        if request.headers['12345'] == 'hello!':
            data = request.get_json()

            entry = CountryModel(id=data['id'], name=data['name'], cca3=data['cca3'],
                                 currency_code=data['currency_code'], currency=data['currency'], capital=data['capital'],
                                 region=data['region'], subregion=data['subregion'],
                                 area=data['area'],
                                 map_url=data['map_url'],
                                 population=data['population'],
                                 flag_url=data['flag_url'])

            db.session.add(entry)
            db.session.commit()
            return 'received', 200
        else:
            return 'Unauthorized', 401

    def get(self):
        return 'Forbidden', 403


class add_neighbour(Resource):
    def post(self):
        if request.headers['12345'] == 'hello!':
            data = request.get_json()

            entry = CountryNeighbour(id=data['id'], country_id=data['country_id'],
                                     neighbour_id=data[
                'neighbour_id'],
                created_at=data['created_at'],
                updated_at=data['updated_at'],)

            db.session.add(entry)
            db.session.commit()

            return 'received', 200
        else:
            return 'Unauthorized', 401

    def get(self):
        return 'Forbidden', 403


class get_country(Resource):
    def get(self, id):
        object = CountryModel.query.filter_by(id=id).first()
        st = ''
        code = 0
        if object:
            st = 'Country List'
            code = 200
            jsonData['message'] = st
            data = {}
            data['list'] = object.to_dict()
            jsonData['data'] = data
            return jsonData, code

        else:
            st = 'Country Not Found'
            code = 404
            jsonData['message'] = st
            data = {}
            jsonData['data'] = data
            return jsonData, code


class get_neighbour(Resource):
    def get(self, id):
        data = {}
        id = str(id)
        jsonData['message'] = 'Country Neighbour'

        # object = CountryModel.query.join(CountryNeighbour, ).filter(CountryNeighbour.neighbour_id == CountryModel.id).filter_by(id = id).all()

        object = CountryModel.query\
            .join(CountryNeighbour, CountryModel.id == CountryNeighbour.country_id)\
            .filter(CountryNeighbour.neighbour_id == id).all()

        alc = []

        for o in object:
            alc.append(o.to_dict())

        data['list'] = alc
        jsonData['data'] = data
        return jsonData, 200


class get_sorted_data(Resource):
    def get(self):

        params = ['a_to_z', 'z_to_a', 'population_high_to_low',
                  'population_low_to_high', 'area_high_to_low', 'area_low_to_high']

        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)

        name = request.args.get('name')
        region = request.args.get('region')
        sub_region = request.args.get('subregion')

        data = request.args.get('sort_by')

        sort_query = ''
        search_query = ''

        if data == params[0]:
            sort_query = '(CountryModel.name)'
        elif data == params[1]:
            sort_query = '(CountryModel.name.desc())'
        elif data == params[2]:
            sort_query = '(CountryModel.population)'
        elif data == params[3]:
            sort_query = '(CountryModel.population.desc())'
        elif data == params[4]:
            sort_query = '(CountryModel.area)'
        elif data == params[5]:
            sort_query = '(CountryModel.area.desc())'

        if name or region or sub_region:
            if name:
                search_query += 'name=name,'
            if region:
                search_query += 'region=region,'
            if sub_region:
                search_query += 'subregion=sub_region'

        code = 'CountryModel.query'

        if search_query or sort_query:
            if search_query:
                code += f'.filter_by({search_query})'
            if sort_query:
                code += f'.order_by{sort_query}'
        else:
            code += '.order_by(CountryModel.id)'

        code += f'.paginate(page={page}, per_page={limit})'

        # print(code)

        count = (page-1)*limit

        object = eval(code)
        data = {}
        jsonData['message'] = 'Country List'
        alc = []
        for o in object:
            count -= 1
            if count > 0:
                continue
            alc.append(o.to_dict())

        data['list'] = alc
        jsonData['data'] = data
        return jsonData, 200


api.add_resource(add_country, '/ac')
api.add_resource(add_neighbour, '/an')

api.add_resource(get_country, '/country/<int:id>')
api.add_resource(get_neighbour, '/country/<int:id>/neighbour')
api.add_resource(get_sorted_data, '/country')


if __name__ == '__main__':
    app.run(debug=True)
