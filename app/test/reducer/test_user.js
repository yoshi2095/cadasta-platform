import {expect} from 'chai';
import {fromJS} from 'immutable';

import user from '../../src/reducer/user';
import Storage from '../test-helper/Storage';

describe('user reducer', () => {
  beforeEach(() => {
    window.localStorage = new Storage();
  });

  it('handles LOGIN_SUCCESS with successful login', () => {
    const state = fromJS({ });

    const action = {
      type: 'LOGIN_SUCCESS',
      response: {
        auth_token: "mskdj8sdh8shadhs"  
      }
    };
    const nextState = user(state, action);

    expect(nextState).to.equal(fromJS({
      auth_token: "mskdj8sdh8shadhs"
    }));

    expect(window.localStorage.getItem('auth_token')).to.equal("mskdj8sdh8shadhs");
  });

  it('handles LOGOUT_SUCCESS', () => {
    const state = fromJS({ auth_token: "mskdj8sdh8shadhs" });
    const action = { type: 'LOGOUT_SUCCESS' };
    const nextState = user(state, action);

    expect(nextState).to.equal(fromJS({ }));

    expect(window.localStorage.getItem('auth_token')).to.be.null;
  });

  it('handles REGISTER_SUCCESS', () => {
    const state = fromJS({ });

    const action = {
      type: 'REGISTER_SUCCESS',
      response: {
        email: "john@beatles.uk",
        email_verified: false,
        first_name: "John",
        last_name: "Lennon",
        username: "john"
      }
    };
    const nextState = user(state, action);

    expect(nextState).to.equal(fromJS({
      email: "john@beatles.uk",
      email_verified: false,
      first_name: "John",
      last_name: "Lennon",
      username: "john"
    }));
  });

  it('handles UPDATEPROFILE_SUCCESS', () => {
    const state = fromJS({ 
      email: "john@beatles.uk",
      first_name: "John",
      last_name: "Lennon",
      username: "john"
    });

    const action = {
      type: 'UPDATEPROFILE_SUCCESS',
      response: {
        email: "paul@beatles.uk",
        first_name: "paul",
        last_name: "McCartney",
        username: "Paul"
      }
    };
    const nextState = user(state, action);

    expect(nextState).to.equal(fromJS({
      email: "paul@beatles.uk",
      first_name: "paul",
      last_name: "McCartney",
      username: "Paul"
    }));
  });

  it('handles USERINFO_SUCCESS', () => {
    const state = fromJS({ });

    const action = {
      type: 'USERINFO_SUCCESS',
      response: {
        email: "paul@beatles.uk",
        first_name: "paul",
        last_name: "McCartney",
        username: "Paul"
      }
    };
    const nextState = user(state, action);

    expect(nextState).to.equal(fromJS({
      email: "paul@beatles.uk",
      first_name: "paul",
      last_name: "McCartney",
      username: "Paul"
    }));
  });
});