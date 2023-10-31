from static.src.feature_extractor import power_features
from static.src.appliance import Appliance
from static.src.signals import Power
from sklearn.preprocessing import StandardScaler
import numpy as np


class ApplianceGuesser:
    def __init__(self, appliances: [Appliance]):
        self.appliances = appliances
        self.appliance_unknown = Appliance(-1, 'Unknown')
        self.feature_scaler = StandardScaler()
        self.feature_data = []  # (appliance, features)
        self._update_features()

    def guess_by_power(self, power: Power):
        features = power_features(power)
        features = self.feature_scaler.transform([features])

        appliance, dist = self._guess_appliance(features)
        appliance = appliance if dist < 0.8 else self.appliance_unknown

        return appliance

    def _update_features(self):
        feature_table = [appliance.features() for appliance in self.appliances]
        feature_table = self.feature_scaler.fit_transform(feature_table)

        self.feature_data = [
            (appliance, features)
            for appliance, features in zip(self.appliances, feature_table)
        ]

    def _guess_appliance(self, features):
        guesses = [
            (appliance, self._euclidean_dist(features, appliance_features))
            for appliance, appliance_features in self.feature_data
        ]
        return min(guesses, key=lambda x: x[1])

    @staticmethod
    def _euclidean_dist(a, b):
        distance = np.linalg.norm(a - b)

        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        return distance / (norm_a + norm_b)
