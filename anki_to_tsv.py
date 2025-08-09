import sqlite3
import zipfile
import tempfile
import os
import json
import csv
import sys
import glob
import re


def extract_anki_db(apkg_path, tmpdir):
    """Extract and find the Anki database file"""
    try:
        with zipfile.ZipFile(apkg_path, 'r') as z:
            z.extractall(tmpdir)

        # Find the database file - Anki 2.1.50+ uses specific filenames
        for filename in os.listdir(tmpdir):
            if filename.startswith('collection') and (filename.endswith('.anki21') or filename.endswith('.anki2')):
                return os.path.join(tmpdir, filename)
            if filename == 'collection.anki21' or filename == 'collection.anki2':
                return os.path.join(tmpdir, filename)

        # If not found, try all files
        for filename in os.listdir(tmpdir):
            filepath = os.path.join(tmpdir, filename)
            if os.path.isfile(filepath) and not filename.endswith(
                    ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.mp3', '.ogg', '.wav', '.ttf')):
                try:
                    with open(filepath, 'rb') as f:
                        header = f.read(16)
                    if header == b'SQLite format 3\x00':
                        return filepath
                except:
                    continue
        return None

    except zipfile.BadZipFile:
        print(f"Error: {apkg_path} is not a valid ZIP file")
        return None
    except Exception as e:
        print(f"Extraction error: {str(e)}")
        return None


def get_models_from_notetypes(conn):
    """Retrieve models from notetypes table (Anki 2.1.50+)"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, json FROM notetypes")
        models = {}
        for mid, name, model_json in cursor.fetchall():
            try:
                model_data = json.loads(model_json)
                fields = [f['name'] for f in model_data['flds']]
                models[mid] = {
                    'name': name,
                    'fields': fields,
                    'field_count': len(fields)
                }
            except (KeyError, json.JSONDecodeError, TypeError) as e:
                print(f"Warning: Could not parse model {mid} - {str(e)}")
                continue
        return models
    except sqlite3.Error:
        return None


def get_models_from_col(conn):
    """Retrieve models from col table (legacy Anki)"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT models FROM col")
        result = cursor.fetchone()
        if not result or not result[0]:
            return None

        models_json = result[0]
        try:
            models_data = json.loads(models_json)
        except json.JSONDecodeError:
            # Try to fix malformed JSON (common in some Anki exports)
            try:
                fixed_json = re.sub(r'(\w+):', r'"\1":', models_json)
                models_data = json.loads(fixed_json)
            except:
                return None

        models = {}
        for mid, mdata in models_data.items():
            try:
                # Handle both string and integer model IDs
                mid_int = int(mid) if isinstance(mid, str) and mid.isdigit() else mid
                fields = [f['name'] for f in mdata['flds']]
                models[mid_int] = {
                    'name': mdata['name'],
                    'fields': fields,
                    'field_count': len(fields)
                }
            except (KeyError, TypeError):
                continue
        return models
    except sqlite3.Error:
        return None


def get_notes(conn, models):
    """Retrieve notes from the database"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, mid, flds FROM notes")
        notes = []

        for nid, mid, flds in cursor.fetchall():
            if mid not in models:
                # Try integer conversion if mid is string
                try:
                    mid_int = int(mid)
                    if mid_int in models:
                        mid = mid_int
                except:
                    pass

                if mid not in models:
                    continue

            model = models[mid]
            fields = flds.split('\x1f')  # Anki field separator

            # Handle field count mismatch
            if len(fields) < model['field_count']:
                fields += [''] * (model['field_count'] - len(fields))
            elif len(fields) > model['field_count']:
                fields = fields[:model['field_count']]

            note_data = {'model': model['name']}
            for i, field_name in enumerate(model['fields']):
                if i < len(fields):
                    note_data[field_name] = fields[i]
                else:
                    note_data[field_name] = ''

            notes.append(note_data)

        return notes

    except sqlite3.Error as e:
        print(f"Database error when retrieving notes: {str(e)}")
        return []


def apkg_to_tsv(apkg_path, tsv_path):
    """Convert Anki APKG to TSV"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = extract_anki_db(apkg_path, tmpdir)
        if not db_path:
            print("Error: Could not find Anki database in package")
            return False

        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row

            # First try modern notetypes table
            models = get_models_from_notetypes(conn)
            if not models:
                print("Trying legacy model extraction...")
                models = get_models_from_col(conn)

            if not models:
                print("Error: Could not retrieve note models")
                # Try to get model names directly from notes
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT mid FROM notes")
                model_ids = [row[0] for row in cursor.fetchall()]
                print(f"Found {len(model_ids)} model IDs in notes: {model_ids}")
                return False

            print(f"Found {len(models)} note models")
            notes = get_notes(conn, models)

            if not notes:
                print("Error: No notes found in database")
                return False

            print(f"Found {len(notes)} notes")

            # Collect all field names
            fieldnames = set(['model'])
            for note in notes:
                fieldnames.update(note.keys())

            # Write TSV
            with open(tsv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f,
                                        fieldnames=sorted(fieldnames),
                                        delimiter='\t',
                                        extrasaction='ignore')
                writer.writeheader()
                writer.writerows(notes)

            return True

        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")
            return False
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Anki Deck to TSV Converter")
        print("Usage: python anki_to_tsv.py <input.apkg> [output.tsv]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else \
        os.path.splitext(input_file)[0] + '.tsv'

    if not os.path.exists(input_file):
        print(f"Error: Input file not found - {input_file}")
        sys.exit(1)

    if apkg_to_tsv(input_file, output_file):
        print(f"Successfully converted {input_file} to {output_file}")
        try:
            line_count = sum(1 for _ in open(output_file, encoding='utf-8'))
            print(f"Exported {line_count - 1} notes (plus header)")
        except:
            print("Output file created")
        sys.exit(0)
    else:
        print("Conversion failed")
        sys.exit(1)