use std::sync::LazyLock;

use anyhow::{anyhow, Context};
use arrow::array::{Array, ArrayData, BinaryArray, LargeBinaryArray, LargeStringArray, StringArray};
use arrow::pyarrow::{FromPyArrow, ToPyArrow};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use tikv_jemallocator::Jemalloc;

#[global_allocator]
static GLOBAL: Jemalloc = Jemalloc;

static TOKIO_RUNTIME: LazyLock<tokio::runtime::Runtime> = LazyLock::new(|| {
    tokio::runtime::Builder::new_multi_thread()
        .enable_all()
        .build()
        .unwrap()
});

#[pymodule]
fn berry_core(py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    env_logger::try_init().ok();

    m.add_function(wrap_pyfunction!(base58_encode_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(base58_decode_string, m)?)?;
    m.add_function(wrap_pyfunction!(get_token_metadata, m)?)?;
    m.add_function(wrap_pyfunction!(get_token_metadata_as_table, m)?)?;
    m.add_function(wrap_pyfunction!(get_pools_token0_token1, m)?)?;
    m.add_function(wrap_pyfunction!(get_pools_token0_token1_as_table, m)?)?;

    Ok(())
}

#[pyfunction]
fn base58_encode_bytes(bytes: &[u8]) -> String {
    bs58::encode(bytes)
        .with_alphabet(bs58::Alphabet::BITCOIN)
        .into_string()
}

#[pyfunction]
fn base58_decode_string(s: &str) -> PyResult<Vec<u8>> {
    bs58::decode(s)
        .with_alphabet(bs58::Alphabet::BITCOIN)
        .into_vec()
        .context("decode bs58")
        .map_err(Into::into)
}

#[pyfunction]
fn get_token_metadata(
    rpc_url: &str,
    addresses: Vec<String>,
    selector: &Bound<'_, PyAny>,
    py: Python<'_>,
) -> PyResult<PyObject> {
    let selector = selector.extract::<cherry_rpc_call::TokenMetadataSelector>()?;
    let token_metadata = TOKIO_RUNTIME.block_on(async {
        cherry_rpc_call::get_token_metadata(rpc_url, addresses, &selector).await
    })?;
    let py_list = PyList::empty(py);

    for metadata in token_metadata {
        let dict = PyDict::new(py);

        match metadata.address {
            Some(address) => dict.set_item("address", address.to_string())?,
            None => dict.set_item("address", py.None())?,
        }

        if selector.decimals {
            match metadata.decimals {
                Some(decimals) => dict.set_item("decimals", decimals)?,
                None => dict.set_item("decimals", py.None())?,
            }
        }

        if selector.symbol {
            match metadata.symbol {
                Some(symbol) => dict.set_item("symbol", symbol)?,
                None => dict.set_item("symbol", py.None())?,
            }
        }

        if selector.name {
            match metadata.name {
                Some(name) => dict.set_item("name", name)?,
                None => dict.set_item("name", py.None())?,
            }
        }

        if selector.total_supply {
            match metadata.total_supply {
                Some(total_supply) => dict.set_item("total_supply", total_supply.to_string())?,
                None => dict.set_item("total_supply", py.None())?,
            }
        }

        py_list.append(dict)?;
    }

    Ok(py_list.into())
}

#[pyfunction]
fn get_token_metadata_as_table(
    rpc_url: &str,
    addresses: Vec<String>,
    selector: &Bound<'_, PyAny>,
    py: Python<'_>,
) -> PyResult<PyObject> {
    let token_metadata = TOKIO_RUNTIME.block_on(async {
        cherry_rpc_call::get_token_metadata(
            rpc_url,
            addresses,
            &selector.extract::<cherry_rpc_call::TokenMetadataSelector>()?,
        )
        .await
    })?;
    let batch = cherry_rpc_call::token_metadata_to_table(
        token_metadata,
        &selector.extract::<cherry_rpc_call::TokenMetadataSelector>()?,
    )?;

    Ok(batch.to_pyarrow(py).context("map result back to pyarrow")?)
}

#[pyfunction]
fn get_pools_token0_token1(
    rpc_url: &str,
    pool_addresses: Vec<String>,
    py: Python<'_>,
) -> PyResult<PyObject> {
    let pool_tokens = TOKIO_RUNTIME.block_on(async {
        cherry_rpc_call::get_pools_token0_token1(rpc_url, pool_addresses).await
    })?;
    let py_list = PyList::empty(py);

    for pool in pool_tokens {
        let dict = PyDict::new(py);

        match pool.pool_address {
            Some(address) => dict.set_item("pool_address", address.to_string())?,
            None => dict.set_item("pool_address", py.None())?,
        }

        match pool.token0 {
            Some(token0) => dict.set_item("token0", token0.to_string())?,
            None => dict.set_item("token0", py.None())?,
        }

        match pool.token1 {
            Some(token1) => dict.set_item("token1", token1.to_string())?,
            None => dict.set_item("token1", py.None())?,
        }

        py_list.append(dict)?;
    }

    Ok(py_list.into())
}

#[pyfunction]
fn get_pools_token0_token1_as_table(
    rpc_url: &str,
    pool_addresses: Vec<String>,
    py: Python<'_>,
) -> PyResult<PyObject> {
    let pool_tokens = TOKIO_RUNTIME.block_on(async {
        cherry_rpc_call::get_pools_token0_token1(rpc_url, pool_addresses).await
    })?;
    let batch = cherry_rpc_call::v2_pool_tokens_to_table(pool_tokens)?;

    Ok(batch.to_pyarrow(py).context("map result back to pyarrow")?)
}