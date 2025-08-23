#
# Copyright (c) 2025 Commonwealth Scientific and Industrial Research Organisation (CSIRO). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file. See the AUTHORS file for names of contributors.
#
import os
import sys
from typing import Any
from pydantic import BaseModel, SkipValidation
import subprocess

from .constants import DEF_IVCAP_URL

class BaseConfig(BaseModel):
    line: SkipValidation[Any]

    @property
    def ivcap_url(self) -> str:
        base_url = os.environ.get("IVCAP_URL")
        if not base_url:
            cmd = ["ivcap", "context", "get", "url"]
            self.line(f"<debug>Running: {' '.join(cmd)} </debug>")
            base_url = subprocess.check_output(cmd).decode().strip()
        if not base_url:
            base_url = DEF_IVCAP_URL
        return base_url

    @property
    def ivcap_jwt(self) -> str:
        jwt = os.environ.get("IVCAP_JWT")
        if not jwt:
            cmd = ["ivcap", "context", "get", "access-token", "--refresh-token"]
            self.line(f"<debug>Running: {' '.join(cmd)} </debug>")
            jwt = subprocess.check_output(cmd).decode().strip()
        if not jwt:
            self.line("<error>ERROR: IVCAP JWT is not set. Please run 'ivcap login' first.</error>")
            sys.exit(1)
        return jwt