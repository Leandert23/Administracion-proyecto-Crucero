class CruceroRouter:
    def db_for_read(self, model, **hints):
        return hints.get("crucero")

    def db_for_write(self, model, **hints):
        return hints.get("crucero")

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == "App":
            return True
        return None
