import pandas as pd
from datetime import datetime


class DBMan(object):

    def __init__(self, config):
        self.unit = DBMan.load_table(config["table"]["unit"]),
        self.weaprof = DBMan.load_table(config["table"]["weaprof"]),
        self.damage = DBMan.load_table(config["table"]["damage"]),
        self.ability = DBMan.load_table(config["table"]["ability"])

    @staticmethod
    def load_table(table_path):
        try:
            table = pd.read_parquet(table_path)
        except FileNotFoundError:
            table = pd.DataFrame()
        return table

    def write(self, warscroll):
        """
        Function to take a warscroll object and store all of the
        relevant info in an organized fashion.
        """
        self._unit_write(warscroll)
        self._weaprof_write(warscroll)
        self._damage_write(warscroll)
        self._ability_write(warscroll)

    def _unit_write(self, warscroll):
        entry = {
          "timestamp" = datetime.now(),
          "alliance" = warscroll.grand_alliance,
          "faction" = warscroll.faction,
          "unit_name" = warscroll.name,
          "points" = warscroll.points,
          "roles" = warscroll.battelfield_role,
          "base_size" = warscroll.base_size,
          "notes" = warscroll.notes,
          "unit_size" = warscroll.unit_size,
          "move" = warscroll.movement,
          "save" = warscroll.save,
          "wounds" = warscroll.wounds,
          "bravery" = warscroll.bravery,
          "fly" = warscroll.fly,
          "mounted" = "mount" in warscroll.text_abilities
        }

