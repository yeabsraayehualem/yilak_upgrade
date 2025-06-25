# def migrate(cr, version):
#     """
#     Migration script to make plan_line_id column nullable in convert_to_po table.
#     """
#     cr.execute("ALTER TABLE convert_to_po ALTER COLUMN plan_line_id DROP NOT NULL;")