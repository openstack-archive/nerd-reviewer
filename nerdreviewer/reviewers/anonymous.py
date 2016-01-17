#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import random

from nerdreviewer import personality
from nerdreviewer import reviewer


class AnonymousReviewer(reviewer.Reviewer):
    PREFIXES = [
        "AnonymousCoward",
        "JohnDoe",
        "JaneDoe",
    ]

    def __init__(self):
        name = random.choice(self.PREFIXES)
        name += str(random.randint(1, 1000))
        super(AnonymousReviewer, self).__init__(name)
        moods = list(personality.Mood)
        mood = random.choice(moods)
        self._mood = mood
        self._personality = {
            mood: 1.0,
        }
        for mood in moods:
            if mood not in self._personality:
                self._personality[mood] = 0.0

    def review(self, a_review):
        pass

    @property
    def description(self):
        mood = self._mood.value.lower()
        lines = [
            "%s is a %s reviewer" % (self.name, mood),
            "",
            "%s will never stop or get tired" % (self.name),
        ]
        return "\n".join(lines)

    @property
    def personality(self):
        """Current personality profile/dict of this reviewer"""
        return self._personality.copy()
