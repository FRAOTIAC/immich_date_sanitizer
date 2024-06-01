import copy
import datetime
import json

import requests
from tqdm import tqdm


class DateSanitizer:
    def __init__(self, api_url, api_key,reset_to_exif_original=False):
        self.api_url = api_url
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'x-api-key': api_key
        }
        self.today = datetime.datetime.now()
        self.reset_to_exif_original = reset_to_exif_original


    def process_records(self):
        print("Fetching and processing data from API...")
        try:
            response = requests.get(self.api_url, headers=self.headers)
            response.raise_for_status()
            records = response.json()

            progress = tqdm(records, desc="Updating records")
            success_count = 0
            fail_count = 0

            for record in progress:
                if self.update_record(record, progress):
                    success_count += 1
                else:
                    fail_count += 1

            print(f"All records processed: {success_count} updated successfully, {fail_count} failed to update.")
        except requests.RequestException as e:
            print(f"Failed to fetch data: {e}")
        except json.JSONDecodeError:
            print("Failed to decode JSON from response")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def update_record(self, record, progress):
        id = record['id']
        original_record = copy.deepcopy(record)

        if self.reset_to_exif_original:
            dateTimeOriginal = self.parse_date(record.get('exifInfo', {}).get('dateTimeOriginal'))
            if dateTimeOriginal:
                reasonable_date = dateTimeOriginal
            else:
                progress.write(f"Record with id: {id} does not have a valid dateTimeOriginal")
                return False
        else:
            if self.has_incorrect_date(record):
                reasonable_date = self.find_most_reasonable_date(record)
                if not reasonable_date:
                    progress.write(f"Record with id: {id} does not have a valid reasonable date")
                    return False
            else:
                progress.write(f"Record with id: {id} has no incorrect dates")
                return True

        update_payload = self.build_update_payload(record, reasonable_date)
        response = requests.put(f"{self.api_url}/{id}", headers=self.headers, data=json.dumps(update_payload))
        if response.status_code == 200:
            self.print_changes(original_record, record, progress, id)
            return True
        else:
            progress.write(f"Failed to update record with id: {id}")
            return False

    def has_incorrect_date(self, record):
        date_keys = ['fileCreatedAt', 'localDateTime', 'fileModifiedAt']

        # Check dates in exifInfo
        exif_info = record.get('exifInfo', {})
        exif_dates = [
            self.parse_date(exif_info.get('dateTimeOriginal')),
            self.parse_date(exif_info.get('modifyDate'))
        ]

        # Check other date keys
        other_dates = [self.parse_date(record.get(key)) for key in date_keys]

        # Combine all dates
        all_dates = exif_dates + other_dates

        for date in all_dates:
            if self.is_incorrect_date(date):
                return True
        return False

    def is_incorrect_date(self, date):
        return date and (date > self.today or date.year < 1970)

    def find_most_reasonable_date(self, record):
        exif_info = record.get('exifInfo', {})
        exif_dates = [
            self.parse_date(exif_info.get('dateTimeOriginal')),
            self.parse_date(exif_info.get('modifyDate'))
        ]

        other_date_keys = ['fileCreatedAt', 'localDateTime', 'fileModifiedAt']
        other_dates = [self.parse_date(record.get(key)) for key in other_date_keys]

        valid_dates = [date for date in (exif_dates + other_dates) if date and date <= self.today]

        if valid_dates:
            min_valid_date = min(valid_dates)
            if min_valid_date.year > 1970:
                return min_valid_date
            else:
                return None
        else:
            return None

    def build_update_payload(self, record, reasonable_date):
        iso_date = reasonable_date.isoformat() + 'Z'

        date_fields = ['fileCreatedAt', 'localDateTime', 'modifyDate']
        for field in date_fields:
            current_date = self.parse_date(record.get(field))
            if self.is_incorrect_date(current_date):
                record[field] = iso_date

        if 'exifInfo' in record:
            exif = record['exifInfo']
            exif_date_fields = ['dateTimeOriginal', 'modifyDate']
            for field in exif_date_fields:
                exif_date = self.parse_date(exif.get(field))
                if self.is_incorrect_date(exif_date):
                    exif[field] = iso_date

        return record

    def print_changes(self, original, updated, progress, record_id):
        changes = []
        for key in original.keys():
            if isinstance(original[key], dict) and isinstance(updated[key], dict):
                changes.extend(self.print_changes(original[key], updated[key], progress, record_id))
            elif original[key] != updated[key]:
                change = f"{key}:\n  from: {original[key]}\n  to:   {updated[key]}"
                changes.append(change)

        if changes:
            progress.write(f"\nChanges in record ID {record_id}:")
            for change in changes:
                progress.write(change)
        return changes

    def parse_date(self, date_str):
        if date_str is None:
            return None
        try:
            return datetime.datetime.fromisoformat(date_str.rstrip('Z'))
        except ValueError:
            return None
