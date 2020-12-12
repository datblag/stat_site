class DatExtDB:
    def get_list(self, patient_id=None, order=None):
        query = self.query.filter(self.is_deleted != 1).order_by(order)
        if patient_id is not None:
            query = query.filter_by(patient_id_ref=patient_id)
        return query

