# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>.

from datetime import datetime
import asyncio

import typer

from bdns.fetch.utils import format_date_for_api_request, format_url
from bdns.fetch.types import Order, Direccion, DescripcionTipoBusqueda
from bdns.fetch.fetch_write import fetch_and_write_paginated
from bdns.fetch.commands import options
from bdns.fetch.endpoints import BDNS_API_ENDPOINT_PARTIDOSPOLITICOS_BUSQUEDA


def partidospoliticos_busqueda(
    ctx: typer.Context,
    num_pages: int = options.num_pages,
    from_page: int = options.from_page,
    pageSize: int = options.pageSize,
    order: Order = options.order,
    direccion: Direccion = options.direccion,
    vpd: str = options.vpd,
    descripcion: str = options.descripcion,
    descripcionTipoBusqueda: DescripcionTipoBusqueda = options.descripcionTipoBusqueda,
    numeroConvocatoria: str = options.numeroConvocatoria,
    codConcesion: str = options.codConcesion,
    fechaDesde: datetime = options.fechaDesde,
    fechaHasta: datetime = options.fechaHasta,
) -> None:
    """
    Fetches data from https://www.infosubvenciones.es/bdnstrans/api/partidospoliticos/busqueda
    """
    params = {
        "pageSize": pageSize,
        "order": order,
        "direccion": direccion,
        "vpd": vpd,
        "descripcion": descripcion,
        "descripcionTipoBusqueda": descripcionTipoBusqueda,
        "numeroConvocatoria": numeroConvocatoria,
        "codConcesion": codConcesion,
        "fechaDesde": format_date_for_api_request(fechaDesde),
        "fechaHasta": format_date_for_api_request(fechaHasta),
    }
    asyncio.run(
        fetch_and_write_paginated(
            url=format_url(BDNS_API_ENDPOINT_PARTIDOSPOLITICOS_BUSQUEDA, params),
            output_file=ctx.obj["output_file"],
            from_page=from_page,
            num_pages=num_pages,
            max_concurrent_requests=ctx.obj["max_concurrent_requests"],
        )
    )
