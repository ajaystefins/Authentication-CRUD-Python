from flask_restx import Resource, Namespace, fields, marshal
from app.database import get_db
from ..exceptions import ValidationException

from ..utils import token_required
import re

product_ns = Namespace('products', description='Product operations')

product_model = product_ns.model('Product', {
    'name': fields.String(required=True, attribute='product_name'),
    'price': fields.Integer(required=True, attribute='product_price'),
    'description': fields.String(required=True, attribute='product_description')
})


@product_ns.route('/')
@product_ns.doc(security='apikey')
class Products(Resource):
    @product_ns.expect(product_model, validate=True)
    @token_required
    @product_ns.response(400, 'mobile or password incorrect')
    def post(self, current_user):
        conn = get_db()
        cursor = conn.cursor()
        sql = "INSERT INTO products(product_name,product_description,product_price) VALUES(%s,  %s, %s)"
        data = (product_ns.payload['name'],
                product_ns.payload['description'], product_ns.payload['price'],)

        cursor.execute(sql, data)
        conn.commit()
        return {'success': True, 'id': cursor.lastrowid}

    @token_required
    @product_ns.marshal_with(product_model)
    def get(self, current_user):
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT product_id,product_name,product_price,product_description FROM products"
        cursor.execute(sql, )
        return cursor.fetchall()


@product_ns.route('/<product_id>')
@product_ns.doc(security='apikey')
class Product(Resource):
    @product_ns.expect(product_model, validate=True)
    @product_ns.response(200, 'Success')
    @product_ns.response(400, 'Product not found')
    @token_required
    def put(self, current_user, product_id):
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT product_id FROM products WHERE product_id=%s"
        data = (product_id,)
        cursor.execute(sql, data)
        cursor.fetchall()
        print(cursor.rowcount)
        if cursor.rowcount < 1:
            return {"success": False, "message": "Product not found"}, 400
        sql = "UPDATE products SET product_name=COALESCE(%s,product_name),product_description=COALESCE(%s,product_description),product_price=COALESCE(%s,product_price) WHERE product_id=%s"
        data = (product_ns.payload['name'],
                product_ns.payload['description'], product_ns.payload['price'], product_id)

        cursor.execute(sql, data)
        conn.commit()
        return {"success": True, "message": "Product updated successfully"}

    @product_ns.response(200, 'Success')
    @product_ns.response(400, 'Product not found')
    @token_required
    def delete(self, current_user, product_id):
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT product_id FROM products WHERE product_id=%s"
        data = (product_id,)
        cursor.execute(sql, data)
        cursor.fetchall()
        print(cursor.rowcount)
        if cursor.rowcount < 1:
            return {"success": False, "message": "Product not found"}, 400
        sql = "DELETE FROM  products WHERE product_id=%s"
        data = (product_id,)
        cursor.execute(sql, data)
        conn.commit()
        return {"success": True, "message": "Product deleted successfully"}
