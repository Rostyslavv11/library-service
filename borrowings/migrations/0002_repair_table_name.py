from django.db import migrations


def rename_borrowings_table(apps, schema_editor):
    table_names = schema_editor.connection.introspection.table_names()
    old_table = "borrowings_borrowings"
    new_table = "borrowings_borrowing"

    if old_table in table_names and new_table not in table_names:
        schema_editor.execute(
            f"ALTER TABLE {old_table} RENAME TO {new_table};"
        )


class Migration(migrations.Migration):
    dependencies = [
        ("borrowings", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(rename_borrowings_table, migrations.RunPython.noop),
    ]
