// Copyright 2015 refractionPOINT
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use a file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/*
Package hcp contains definitions and helpers specific to the operation of the 
LimaCharlie Host Common Platform.
*/
package hcp

import (
	"fmt"
	"github.com/google/uuid"
	"strconv"
	"strings"
)

// Module IDs of common HCP modules
const (
	ModuleIDHcp        = 1
	ModuleIDHbs        = 2
	ModuleIDKernelAcq = 5
)

// Command IDs of HCP commands
const (
	LoadModule     = 1
	UnloadModule   = 2
	SetHcpID      = 3
	SetGlobalTime = 4
	Quit            = 5
)

// AgentID is the logical representation of the ID components used
// to identify a specific sensor and its basic characteristics
type AgentID struct {
	Oid          uuid.UUID
	Iid          uuid.UUID
	Sid          uuid.UUID
	Platform     uint32
	Architecture uint32
}

// IsAbsolute returns true if none of the components of the AgentID are wildcards (0)
func (a AgentID) IsAbsolute() bool {
	var emptyUUID uuid.UUID
	if a.Oid == emptyUUID ||
		a.Iid == emptyUUID ||
		a.Platform == 0 ||
		a.Architecture == 0 {
		return false
	}
	return true
}

// IsSidWild returns true if the SensorId component of the AgentID is a wildcard
func (a AgentID) IsSidWild() bool {
	var emptyUUID uuid.UUID
	return a.Sid == emptyUUID
}

func uuidAsWildString(id uuid.UUID) string {
	var emptyUUID uuid.UUID
	if id == emptyUUID {
		return "0"
	}
	return id.String()
}

// ToString converts the AgentID to its standardized string representation
func (a AgentID) ToString() string {

	return fmt.Sprintf("%s.%s.%s.%x.%x",
		uuidAsWildString(a.Oid),
		uuidAsWildString(a.Iid),
		uuidAsWildString(a.Sid),
		a.Platform,
		a.Architecture)
}

// FromString converts the standardized string representation of an AgentID into an AgentID
func (a AgentID) FromString(s string) bool {
	var err error
	var emptyUUID uuid.UUID
	var tmp64 uint64
	components := strings.Split(s, ".")
	if len(components) != 5 {
		return false
	}

	if components[0] == "0" {
		a.Oid = emptyUUID
	} else if a.Oid, err = uuid.Parse(components[0]); err != nil {
		return false
	}

	if components[1] == "0" {
		a.Iid = emptyUUID
	} else if a.Iid, err = uuid.Parse(components[1]); err != nil {
		return false
	}

	if components[2] == "0" {
		a.Sid = emptyUUID
	} else if a.Sid, err = uuid.Parse(components[2]); err != nil {
		return false
	}

	if tmp64, err = strconv.ParseUint(components[3], 16, 32); err != nil {
		return false
	}
	a.Platform = uint32(tmp64)

	if tmp64, err = strconv.ParseUint(components[3], 16, 32); err != nil {
		return false
	}
	a.Architecture = uint32(tmp64)

	return true
}

// Matches returns true if both AgentIDs are equal (or wildcarded) in all components
func (a AgentID) Matches(compareTo AgentID) bool {
	var emptyUUID uuid.UUID
	if (a.Oid == emptyUUID || compareTo.Oid == emptyUUID || a.Oid == compareTo.Oid) &&
		(a.Iid == emptyUUID || compareTo.Iid == emptyUUID || a.Iid == compareTo.Iid) &&
		(a.Sid == emptyUUID || compareTo.Sid == emptyUUID || a.Sid == compareTo.Sid) &&
		(a.Platform == 0 || compareTo.Platform == 0 || a.Platform == compareTo.Platform) &&
		(a.Architecture == 0 || compareTo.Architecture == 0 || a.Architecture == compareTo.Architecture) {
		return true
	}

	return false
}
